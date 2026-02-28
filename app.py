import streamlit as st
import json
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador ENEM",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 800px; }

    /* Cards de área */
    .area-card {
        background: #1a1d2e;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }

    /* Questão */
    .question-box {
        background: #1a1d2e;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        font-size: 16px;
        line-height: 1.8;
        color: #e0d8cc;
    }

    /* Explicação */
    .explicacao-box {
        background: #0d2218;
        border: 1px solid #1e6641;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 12px;
        color: #7dd4a8;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Badge de área */
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }

    /* Resultado */
    .result-score {
        text-align: center;
        font-size: 80px;
        font-weight: 700;
        line-height: 1;
        margin: 10px 0;
    }

    /* Progresso */
    .progress-label {
        font-size: 13px;
        color: #6b7280;
        text-align: right;
        margin-bottom: 4px;
    }

    /* Alternativa correta/errada */
    .alt-correta {
        background: #0d2218 !important;
        border: 1px solid #22c55e !important;
        color: #22c55e !important;
    }
    .alt-errada {
        background: #2d0f0f !important;
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }

    /* Ocultar menu do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* Título principal */
    h1 { font-size: 2.8rem !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ──────────────────────────────────────────────────────────────
AREA_CORES = {
    "Linguagens": "#f97316",
    "Ciências Humanas": "#8b5cf6",
    "Ciências da Natureza": "#10b981",
    "Matemática": "#3b82f6",
}
AREA_ICONES = {
    "Linguagens": "✍️",
    "Ciências Humanas": "🏛️",
    "Ciências da Natureza": "🔬",
    "Matemática": "📐",
}
LETRAS = ["A", "B", "C", "D", "E"]

# ── Carregamento de perguntas ───────────────────────────────────────────────
@st.cache_data
def carregar_perguntas():
    caminho = Path(__file__).parent / "perguntas.json"
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()

# ── Inicialização de estado ─────────────────────────────────────────────────
def init_state():
    defaults = {
        "tela": "home",               # home | quiz | resultado
        "areas_selecionadas": list(AREA_CORES.keys()),
        "questoes_ativas": [],
        "indice_atual": 0,
        "respostas": {},              # {indice: idx_escolhido}
        "mostrar_explicacao": False,
        "historico": [],              # lista de resultados anteriores
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ─────────────────────────────────────────────────────────────────
def iniciar_simulado():
    qs = [q for q in PERGUNTAS if q["area"] in st.session_state.areas_selecionadas]
    random.shuffle(qs)
    st.session_state.questoes_ativas = qs
    st.session_state.indice_atual = 0
    st.session_state.respostas = {}
    st.session_state.mostrar_explicacao = False
    st.session_state.tela = "quiz"

def responder(idx_alternativa):
    st.session_state.respostas[st.session_state.indice_atual] = idx_alternativa
    st.session_state.mostrar_explicacao = True

def proxima_questao():
    if st.session_state.indice_atual < len(st.session_state.questoes_ativas) - 1:
        st.session_state.indice_atual += 1
        st.session_state.mostrar_explicacao = False
    else:
        finalizar()

def finalizar():
    qs = st.session_state.questoes_ativas
    respostas = st.session_state.respostas
    acertos = sum(1 for i, q in enumerate(qs) if respostas.get(i) == q["correta"])
    total = len(qs)
    pct = round(acertos / total * 100) if total else 0

    # Salva no histórico
    st.session_state.historico.append({
        "acertos": acertos,
        "total": total,
        "pct": pct,
        "areas": list(st.session_state.areas_selecionadas),
    })
    st.session_state.tela = "resultado"

def calcular_por_area():
    qs = st.session_state.questoes_ativas
    respostas = st.session_state.respostas
    dados = {}
    for area in st.session_state.areas_selecionadas:
        area_qs = [(i, q) for i, q in enumerate(qs) if q["area"] == area]
        acertos = sum(1 for i, q in area_qs if respostas.get(i) == q["correta"])
        total = len(area_qs)
        score = round(acertos / total * 1000) if total else 0
        dados[area] = {"acertos": acertos, "total": total, "score": score}
    return dados

# ══════════════════════════════════════════════════════════════════════════════
# TELA: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.tela == "home":
    st.markdown("## 🎓 Simulador ENEM")
    st.markdown("**40 questões · 4 áreas · Análise por competência**")
    st.divider()

    st.markdown("#### Selecione as áreas")
    cols = st.columns(2)
    for i, (area, cor) in enumerate(AREA_CORES.items()):
        with cols[i % 2]:
            selecionado = area in st.session_state.areas_selecionadas
            qtd = sum(1 for q in PERGUNTAS if q["area"] == area)
            label = f"{AREA_ICONES[area]} {area}  •  {qtd} questões"
            checked = st.checkbox(label, value=selecionado, key=f"cb_{area}")
            if checked and area not in st.session_state.areas_selecionadas:
                st.session_state.areas_selecionadas.append(area)
            elif not checked and area in st.session_state.areas_selecionadas:
                if len(st.session_state.areas_selecionadas) > 1:
                    st.session_state.areas_selecionadas.remove(area)

    total_qs = sum(1 for q in PERGUNTAS if q["area"] in st.session_state.areas_selecionadas)
    st.markdown(f"**{total_qs} questões selecionadas**")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Iniciar Simulado", use_container_width=True, type="primary"):
            iniciar_simulado()
            st.rerun()

    # Histórico
    if st.session_state.historico:
        st.divider()
        st.markdown("#### 📊 Histórico de simulados")
        hist_df = pd.DataFrame(st.session_state.historico)
        hist_df.index = [f"Simulado {i+1}" for i in range(len(hist_df))]
        hist_df.columns = ["Acertos", "Total", "Percentual (%)", "Áreas"]
        st.dataframe(hist_df[["Acertos", "Total", "Percentual (%)"]], use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TELA: QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.tela == "quiz":
    qs = st.session_state.questoes_ativas
    idx = st.session_state.indice_atual
    q = qs[idx]
    total = len(qs)

    # Cabeçalho com progresso
    col_prog, col_num = st.columns([5, 1])
    with col_prog:
        st.progress((idx + 1) / total)
    with col_num:
        st.markdown(f"<div style='text-align:right;font-size:13px;color:#6b7280;padding-top:6px'>{idx+1}/{total}</div>", unsafe_allow_html=True)

    # Badges de área / competência
    cor = AREA_CORES[q["area"]]
    st.markdown(
        f"<span class='badge' style='background:{cor}22;color:{cor};border:1px solid {cor}44'>"
        f"{AREA_ICONES[q['area']]} {q['area']}</span>"
        f"<span class='badge' style='background:#ffffff10;color:#9ca3af;border:1px solid #2a2228'>"
        f"{q['competencia']}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Enunciado
    st.markdown(
        f"<div class='question-box'>{q['enunciado'].replace(chr(10), '<br>')}</div>",
        unsafe_allow_html=True,
    )

    # Alternativas
    respondido = st.session_state.mostrar_explicacao
    resposta_dada = st.session_state.respostas.get(idx)

    for i, alt in enumerate(q["alternativas"]):
        letra = LETRAS[i]
        texto = f"**{letra})** {alt}"

        if respondido:
            if i == q["correta"]:
                st.success(f"✅ {letra}) {alt}")
            elif i == resposta_dada and i != q["correta"]:
                st.error(f"❌ {letra}) {alt}")
            else:
                st.markdown(f"<div style='padding:10px 14px;border-radius:8px;background:#16181f;color:#6b7280;margin-bottom:6px'>{letra}) {alt}</div>", unsafe_allow_html=True)
        else:
            if st.button(f"{letra}) {alt}", key=f"alt_{idx}_{i}", use_container_width=True):
                responder(i)
                st.rerun()

    # Explicação
    if respondido:
        st.markdown(
            f"<div class='explicacao-box'>💡 <strong>Explicação:</strong><br>{q['explicacao']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")
        col1, col2 = st.columns([3, 1])
        with col2:
            label_btn = "Próxima →" if idx < total - 1 else "Ver Resultado 🏆"
            if st.button(label_btn, type="primary", use_container_width=True):
                proxima_questao()
                st.rerun()

    # Botão de abandonar
    with st.expander("⚙️ Opções"):
        if st.button("🏠 Voltar ao início", use_container_width=True):
            st.session_state.tela = "home"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TELA: RESULTADO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.tela == "resultado":
    qs = st.session_state.questoes_ativas
    respostas = st.session_state.respostas
    acertos = sum(1 for i, q in enumerate(qs) if respostas.get(i) == q["correta"])
    total = len(qs)
    pct = round(acertos / total * 100) if total else 0

    # Score principal
    cor_pct = "#10b981" if pct >= 70 else "#f97316" if pct >= 50 else "#ef4444"
    emoji_res = "🎯" if pct >= 70 else "📈" if pct >= 50 else "📚"
    msg_res = "Excelente desempenho!" if pct >= 70 else "Bom, continue praticando!" if pct >= 50 else "Precisa reforçar os estudos."

    st.markdown(f"<div class='result-score' style='color:{cor_pct}'>{pct}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;color:#6b7280;margin-bottom:4px'>{acertos} de {total} questões corretas</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;font-size:18px;margin-bottom:20px'>{emoji_res} {msg_res}</div>", unsafe_allow_html=True)
    st.divider()

    # ── Cards por área ──────────────────────────────────────────────────────
    dados_area = calcular_por_area()
    st.markdown("#### 📊 Desempenho por área")

    cols = st.columns(len(dados_area))
    for i, (area, d) in enumerate(dados_area.items()):
        with cols[i]:
            cor = AREA_CORES[area]
            icone = AREA_ICONES[area]
            st.markdown(
                f"<div style='background:#1a1d2e;border-radius:12px;padding:14px;border-top:3px solid {cor};text-align:center'>"
                f"<div style='font-size:22px'>{icone}</div>"
                f"<div style='font-size:11px;color:#6b7280;margin-top:4px'>{area.split()[0]}</div>"
                f"<div style='font-size:28px;font-weight:700;color:{cor};margin:4px 0'>{d['score']}</div>"
                f"<div style='font-size:12px;color:#4b5563'>{d['acertos']}/{d['total']} acertos</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("")

    # ── Gráfico de barras ───────────────────────────────────────────────────
    labels = [a.split()[0] for a in dados_area]
    scores = [d["score"] for d in dados_area.values()]
    cores = [AREA_CORES[a] for a in dados_area]

    fig_bar = go.Figure(go.Bar(
        x=labels, y=scores,
        marker_color=cores,
        text=scores, textposition="outside",
        textfont=dict(size=13, color="white"),
    ))
    fig_bar.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font_color="white", height=280,
        yaxis=dict(range=[0, 1100], showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        margin=dict(t=30, b=20, l=10, r=10),
        title=dict(text="Score por área (0–1000)", font=dict(size=13, color="#9ca3af"), x=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Radar ───────────────────────────────────────────────────────────────
    areas_radar = list(dados_area.keys())
    pcts_radar = [round(d["acertos"] / d["total"] * 100) if d["total"] else 0 for d in dados_area.values()]

    fig_radar = go.Figure(go.Scatterpolar(
        r=pcts_radar + [pcts_radar[0]],
        theta=[a.split()[0] for a in areas_radar] + [areas_radar[0].split()[0]],
        fill="toself",
        fillcolor="rgba(249,115,22,0.15)",
        line=dict(color="#f97316", width=2),
    ))
    fig_radar.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font_color="white", height=320,
        polar=dict(
            bgcolor="#1a1d2e",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="#2a2d3e"),
            angularaxis=dict(gridcolor="#2a2d3e"),
        ),
        margin=dict(t=30, b=30, l=30, r=30),
        title=dict(text="Radar de competências (%)", font=dict(size=13, color="#9ca3af"), x=0),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Áreas fracas ────────────────────────────────────────────────────────
    areas_fracas = [a for a, d in dados_area.items() if d["score"] < 600 and d["total"] > 0]
    if areas_fracas:
        st.divider()
        st.markdown("#### 📌 Foque seus estudos")
        for area in areas_fracas:
            cor = AREA_CORES[area]
            icone = AREA_ICONES[area]
            st.markdown(
                f"<div style='background:#0d1422;border-left:3px solid {cor};border-radius:8px;padding:14px 18px;margin-bottom:8px'>"
                f"<strong style='color:{cor}'>{icone} {area}</strong><br>"
                f"<span style='color:#4b5563;font-size:13px'>Score abaixo de 600. Revise os fundamentos e resolva mais simulados nesta área.</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Revisão de questões ─────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 🔍 Revisão de questões")
    for i, q in enumerate(qs):
        acertou = respostas.get(i) == q["correta"]
        icone_q = "✅" if acertou else "❌"
        cor_q = AREA_CORES[q["area"]]
        with st.expander(f"{icone_q} Q{i+1} · {q['area']} — {q['competencia']}"):
            st.markdown(f"**{q['enunciado']}**")
            st.markdown("")
            for j, alt in enumerate(q["alternativas"]):
                letra = LETRAS[j]
                if j == q["correta"]:
                    st.success(f"✅ {letra}) {alt}")
                elif j == respostas.get(i) and j != q["correta"]:
                    st.error(f"❌ {letra}) {alt} ← sua resposta")
                else:
                    st.markdown(f"{letra}) {alt}")
            st.markdown(f"<div class='explicacao-box'>💡 {q['explicacao']}</div>", unsafe_allow_html=True)

    # ── Botões finais ───────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↺ Novo simulado", use_container_width=True):
            iniciar_simulado()
            st.rerun()
    with col2:
        if st.button("🏠 Início", use_container_width=True, type="primary"):
            st.session_state.tela = "home"
            st.rerun()
