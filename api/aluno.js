/**
 * Backend do Simulador ENEM na Vercel: cadastro de alunos, link de convite e
 * telemetria, gravando no mesmo Supabase do app Streamlit (banco.py).
 *
 * A chave do Supabase fica SÓ no servidor, nas variáveis de ambiente
 * SUPABASE_URL e SUPABASE_KEY do projeto na Vercel. O navegador nunca a vê.
 *
 * Uso: POST /api/aluno  { "acao": "buscar" | "cadastrar" | "ref" | "evento" | "indicados", ... }
 */
const TBL_CADASTRO = "tbl_cadastro";
const TBL_TELEMETRIA = "tbl_telemetria_acesso";
const TBL_COMPARTILHAMENTO = "tbl_compartilhamento";
const EVENTOS = new Set(["acesso", "login", "login_falhou", "cadastro", "inicio_simulado", "fim_simulado", "logout"]);
const RE_EMAIL = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const RE_UUID = /^[0-9a-f-]{36}$/i;

const normalizarEmail = (e) => String(e || "").trim().toLowerCase();
const normalizarCodigo = (c) => { c = String(c || "").trim().toUpperCase(); return /^[A-Z0-9]{4,16}$/.test(c) ? c : null; };
const idValido = (v) => (typeof v === "number" && Number.isInteger(v)) || (typeof v === "string" && (/^\d{1,18}$/.test(v) || RE_UUID.test(v)));
const texto = (v, max) => (v == null ? null : String(v).slice(0, max) || null);

function sb(path, { method = "GET", body, prefer, headers = {} } = {}) {
  const url = process.env.SUPABASE_URL.replace(/\/+$/, "") + "/rest/v1/" + path;
  const h = { apikey: process.env.SUPABASE_KEY, Accept: "application/json", ...headers };
  if (!process.env.SUPABASE_KEY.startsWith("sb_")) h.Authorization = `Bearer ${process.env.SUPABASE_KEY}`;
  if (body !== undefined) h["Content-Type"] = "application/json";
  if (prefer) h.Prefer = prefer;
  return fetch(url, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(10000) });
}
async function sbJson(path, opts) {
  const r = await sb(path, opts);
  const t = await r.text();
  if (!r.ok) { const e = new Error(`Supabase HTTP ${r.status}: ${t.slice(0, 200)}`); e.status = r.status; throw e; }
  return t ? JSON.parse(t) : null;
}

// ── Contexto do acesso (mesma lógica de banco.py) ─────────────────────────
function analisarUA(ua) {
  ua = ua || "";
  let dispositivo;
  if (!ua) dispositivo = "desconhecido";
  else if (/bot|crawl|spider|slurp|headless/i.test(ua)) dispositivo = "bot";
  else if (/iPad|Tablet/.test(ua) || (ua.includes("Android") && !ua.includes("Mobile"))) dispositivo = "tablet";
  else if (/Mobi|iPhone|iPod|Android/.test(ua)) dispositivo = "mobile";
  else dispositivo = "desktop";
  const so = [[/Windows/, "Windows"], [/Android/, "Android"], [/iPhone|iPad|iPod/, "iOS"], [/Mac OS X|Macintosh/, "macOS"], [/CrOS/, "ChromeOS"], [/Linux/, "Linux"]].find(([re]) => re.test(ua));
  const navs = [[/Edg(?:e|A|iOS)?\/([\d.]+)/, "Edge"], [/OPR\/([\d.]+)/, "Opera"], [/SamsungBrowser\/([\d.]+)/, "Samsung Internet"], [/Firefox\/([\d.]+)|FxiOS\/([\d.]+)/, "Firefox"], [/Chrome\/([\d.]+)|CriOS\/([\d.]+)/, "Chrome"], [/Version\/([\d.]+).*Safari/, "Safari"]];
  let navegador = null, versao = null;
  for (const [re, nome] of navs) { const m = ua.match(re); if (m) { navegador = nome; versao = m.slice(1).find(Boolean) || null; break; } }
  return { dispositivo, sistema_operacional: so ? so[1] : null, navegador, versao_navegador: versao };
}
function contexto(req, cli = {}) {
  const ua = req.headers["user-agent"] || "";
  const ip = String(req.headers["x-forwarded-for"] || req.headers["x-real-ip"] || "").split(",")[0].trim() || null;
  return {
    ip, user_agent: ua || null, ...analisarUA(ua),
    idioma: texto(cli.idioma, 20) || String(req.headers["accept-language"] || "").split(",")[0] || null,
    fuso_horario: texto(cli.fuso_horario, 60),
    url_acessada: texto(cli.url, 500),
    origem_referrer: texto(cli.referrer, 500),
  };
}

// Só devolve ao navegador o necessário para a sessão (sem celular/idade de terceiros).
const publico = (c) => c && ({ id: c.id, nome_completo: c.nome_completo, email: c.email, ativo: c.ativo !== false, codigo_indicacao: c.codigo_indicacao || "" });

async function buscarCadastro(email) {
  const d = await sbJson(`${TBL_CADASTRO}?select=*&email=eq.${encodeURIComponent(email)}&limit=1`);
  return d && d[0] ? d[0] : null;
}

const acoes = {
  async buscar({ email }) {
    email = normalizarEmail(email);
    if (!RE_EMAIL.test(email)) return [400, { erro: "E-mail inválido" }];
    return [200, { cadastro: publico(await buscarCadastro(email)) }];
  },

  async cadastrar({ nome, email, celular, idade, sexo, ref }) {
    email = normalizarEmail(email);
    nome = String(nome || "").trim();
    celular = String(celular || "").replace(/\D/g, "");
    if (!RE_EMAIL.test(email)) return [400, { erro: "E-mail inválido" }];
    if (!nome || nome.length > 120) return [400, { erro: "Informe seu nome" }];
    if (celular && !/^\d{11}$/.test(celular)) return [400, { erro: "Celular deve conter 11 dígitos" }];
    const idadeN = String(idade ?? "").trim() ? parseInt(idade, 10) : null;
    if (idadeN != null && !(idadeN >= 1 && idadeN <= 120)) return [400, { erro: "Idade deve ser um número entre 1 e 120" }];
    if (!["Masculino", "Feminino"].includes(sexo)) return [400, { erro: "Selecione um sexo" }];

    // O dono do link é conferido aqui, a partir da visita registrada — não do que o navegador diz.
    let visita = null;
    if (ref && idValido(ref.compartilhamento_id)) {
      const v = await sbJson(`${TBL_COMPARTILHAMENTO}?select=id,cadastro_origem_id,codigo_indicacao,cadastro_indicado_id&id=eq.${encodeURIComponent(ref.compartilhamento_id)}&limit=1`).catch(() => null);
      if (v && v[0] && !v[0].cadastro_indicado_id) visita = v[0];
    }
    let cad, novo = true;
    try {
      const d = await sbJson(TBL_CADASTRO, {
        method: "POST", prefer: "return=representation",
        body: { nome_completo: nome, email, celular: celular || null, idade: idadeN, sexo, indicado_por: visita ? visita.cadastro_origem_id : null },
      });
      cad = d[0];
    } catch (e) {
      cad = await buscarCadastro(email); // corrida: outro acesso cadastrou o mesmo e-mail
      if (!cad) throw e;
      novo = false;
    }
    const indicado = !!visita && novo && String(cad.indicado_por) === String(visita.cadastro_origem_id);
    if (indicado) {
      await sb(`${TBL_COMPARTILHAMENTO}?id=eq.${encodeURIComponent(visita.id)}`, {
        method: "PATCH", body: { cadastro_indicado_id: cad.id, data_hora_cadastro_indicado: new Date().toISOString() },
      }).catch(() => null);
    }
    return [200, { cadastro: publico(cad), novo, indicado, codigo_ref: indicado ? visita.codigo_indicacao : null }];
  },

  async ref({ codigo, sessao_id, ctx }, req) {
    codigo = normalizarCodigo(codigo);
    if (!codigo) return [200, { ref: null }];
    const dono = await sbJson(`${TBL_CADASTRO}?select=id&codigo_indicacao=eq.${codigo}&limit=1`);
    if (!dono || !dono[0]) return [200, { ref: null }];
    const c = contexto(req, ctx);
    const d = await sbJson(TBL_COMPARTILHAMENTO, {
      method: "POST", prefer: "return=representation",
      body: { codigo_indicacao: codigo, cadastro_origem_id: dono[0].id, sessao_id: texto(sessao_id, 64), ip: c.ip, user_agent: c.user_agent, dispositivo: c.dispositivo, sistema_operacional: c.sistema_operacional, navegador: c.navegador, origem_referrer: c.origem_referrer },
    });
    return [200, { ref: { compartilhamento_id: d[0].id, codigo } }];
  },

  async evento({ tipo_evento, cadastro_id, email, sucesso = true, sessao_id, duracao_segundos, detalhes, ctx }, req) {
    if (!EVENTOS.has(tipo_evento)) return [400, { erro: "evento inválido" }];
    const det = detalhes && typeof detalhes === "object" ? detalhes : {};
    if (JSON.stringify(det).length > 4000) return [400, { erro: "detalhes grandes demais" }];
    await sbJson(TBL_TELEMETRIA, {
      method: "POST", prefer: "return=minimal",
      body: {
        tipo_evento, cadastro_id: idValido(cadastro_id) ? cadastro_id : null, email_informado: normalizarEmail(email) || null,
        sucesso: !!sucesso, sessao_id: texto(sessao_id, 64),
        duracao_segundos: Number.isFinite(duracao_segundos) ? Math.max(0, Math.round(duracao_segundos)) : null,
        detalhes: det, ...contexto(req, ctx),
      },
    });
    return [200, { ok: true }];
  },

  async indicados({ cadastro_id }) {
    if (!idValido(cadastro_id)) return [200, { total: 0 }];
    const r = await sb(`${TBL_CADASTRO}?select=id&indicado_por=eq.${encodeURIComponent(cadastro_id)}`, { prefer: "count=exact", headers: { Range: "0-0" } });
    const total = parseInt(String(r.headers.get("content-range") || "").split("/")[1], 10);
    return [200, { total: Number.isFinite(total) ? total : 0 }];
  },
};

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ erro: "use POST" });
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
    return res.status(503).json({ erro: "sem_banco", mensagem: "Configure SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente da Vercel." });
  }
  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch { body = null; } }
  if (!body || typeof body !== "object" || !acoes[body.acao]) return res.status(400).json({ erro: "ação inválida" });
  try {
    const [status, out] = await acoes[body.acao](body, req);
    return res.status(status).json(out);
  } catch (e) {
    console.error(`[aluno:${body.acao}]`, e.message);
    return res.status(502).json({ erro: "banco_indisponivel", mensagem: "Não foi possível falar com o banco de dados agora." });
  }
};
