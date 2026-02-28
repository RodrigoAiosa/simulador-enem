import streamlit as st
import json
import random
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador ENEM",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');
/* ── Reset & base ── */
html, body, [class*="css"] {
    background-color: #0a0a0f !important;
    color: #e8e0d0;
}
.main { background-color: #0a0a0f !important; }
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
    max-width: 820px !important;
}
/* ── Fundo com grid sutil ── */
.main::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(255,255,255,0.025) 40px, rgba(255,255,255,0.025) 41px),
        repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(255,255,255,0.025) 40px, rgba(255,255,255,0.025) 41px);
    pointer-events: none;
    z-index: 0;
}
/* ── Gradiente de fundo ── */
.main::after {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 15% 10%, rgba(26,10,46,0.9) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 85% 80%, rgba(10,26,26,0.8) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}
/* ── Ocultar elementos Streamlit ── */
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
/* ── Títulos ── */
.titulo-preparatorio {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    letter-spacing: 6px;
    color: #f97316;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 16px;
}
.titulo-enem {
    font-family: 'EB Garamond', serif;
    font-size: clamp(56px, 10vw, 96px);
    font-weight: 700;
    color: #f0e8d8;
    text-align: center;
    line-height: 1;
    text-shadow: 0 0 80px rgba(249,115,22,0.15);
    margin: 0;
}
.titulo-simulador {
    font-family: 'EB Garamond', serif;
    font-size: clamp(28px, 5vw, 48px);
    font-weight: 400;
    font-style: italic;
    color: #f97316;
    text-align: center;
    line-height: 1.2;
    margin-bottom: 20px;
}
.subtitulo {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: #6b6050;
    text-align: center;
    margin-bottom: 40px;
    letter-spacing: 0.3px;
}
/* ── Label de seção ── */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 4px;
    color: #4a4038;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 16px;
}
/* ── Cards de área ── */
.area-card {
    background: rgba(255,255,255,0.03);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid;
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}
.area-card:hover { background: rgba(255,255,255,0.05); }
.area-icon { font-size: 32px; flex-shrink: 0; }
.area-name {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.area-count {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #3a3028;
    margin-top: 2px;
}
.area-check {
    margin-left: auto;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
}
/* ── Total selecionado ── */
.total-label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #4a4038;
    text-align: center;
    margin-bottom: 20px;
}
/* ── Botão principal ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 14px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: #f97316 !important;
    color: #0a0a0f !important;
    box-shadow: 0 0 40px rgba(249,115,22,0.35) !important;
    padding: 18px 64px !important;
    font-size: 15px !important;
}
.stButton > button[kind="primary"]:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 0 60px rgba(249,115,22,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #f97316 !important;
    border: 1px solid #f97316 !important;
}
/* ── Barra de progresso ── */
.stProgress > div > div {
    background: #1a1812 !important;
    border-radius: 4px !important;
    height: 4px !important;
}
.stProgress > div > div > div {
    border-radius: 4px !important;
}
/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
    font-family: 'Inter', sans-serif;
}
/* ── Caixa de questão ── */
.question-box {
    background: #0f0f18;
    border: 1px solid #2a2228;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 20px;
    font-family: 'EB Garamond', serif;
    font-size: 17px;
    line-height: 1.85;
    color: #d8d0c0;
}
/* ── Alternativas ── */
.alt-btn {
    background: #0f0f18;
    border: 1px solid #2a2228;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #b8b0a0;
    line-height: 1.55;
    cursor: pointer;
    transition: all 0.15s;
    width: 100%;
    text-align: left;
}
.alt-btn:hover { background: rgba(255,255,255,0.04); border-color: #4a4248; }
.alt-correta {
    background: rgba(16,185,129,0.08) !important;
    border-color: #10b981 !important;
    color: #10b981 !important;
}
.alt-errada {
    background: rgba(239,68,68,0.08) !important;
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}
.alt-neutra { opacity: 0.4; }
/* ── Explicação ── */
.explicacao-box {
    background: #0a1a0f;
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-top: 4px;
    margin-bottom: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    line-height: 1.75;
    color: #7dd4a8;
}
.explicacao-titulo {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #10b981;
    margin-bottom: 8px;
    font-weight: 600;
}
/* ── Score resultado ── */
.result-pct {
    font-family: 'EB Garamond', serif;
    font-size: 96px;
    font-weight: 700;
    text-align: center;
    line-height: 1;
}
.result-sub {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: #6a6058;
    text-align: center;
    margin-top: 8px;
}
.result-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 6px 20px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    margin-top: 12px;
}
/* ── Card de score por área ── */
.score-card {
    background: #0f0f18;
    border-radius: 16px;
    padding: 18px 20px;
    text-align: center;
    height: 100%;
}
.score-card-area {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    margin-top: 6px;
}
.score-card-value {
    font-family: 'EB Garamond', serif;
    font-size: 36px;
    font-weight: 700;
    margin: 4px 0;
}
.score-card-acertos {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #4a4038;
}
/* ── Sugestão área fraca ── */
.area-fraca {
    background: #080d18;
    border-left: 3px solid;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
}
.area-fraca-nome {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}
.area-fraca-desc {
    font-size: 12px;
    color: #3a4858;
    line-height: 1.6;
}
/* ── Revisão expander ── */
.st-expander {
    background: #0f0f18 !important;
    border: 1px solid #2a2228 !important;
    border-radius: 12px !important;
}
/* ── Histórico ── */
.hist-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: #0f0f18;
    border-radius: 10px;
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #8a8070;
}
/* ── Botões toggle de área ── */
[data-testid="stButton"] button {
    font-size: 11px !important;
    padding: 4px 10px !important;
    height: auto !important;
    margin-top: -4px !important;
    margin-bottom: 8px !important;
    opacity: 0.45 !important;
    border-radius: 8px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid #2a2228 !important;
    color: #5a5048 !important;
    letter-spacing: 0.5px !important;
    text-transform: none !important;
    font-weight: 400 !important;
}
/* ── Botão primário (Iniciar Simulado, Próxima, Resultado) ── */
[data-testid="stButton"] button[kind="primary"],
button[kind="primary"] {
    background: #f97316 !important;
    color: #0a0a0f !important;
    box-shadow: 0 0 40px rgba(249,115,22,0.35) !important;
    font-size: 15px !important;
    padding: 14px 32px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    opacity: 1 !important;
    border: none !important;
    border-radius: 14px !important;
    margin-top: 0 !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 0 60px rgba(249,115,22,0.5) !important;
    opacity: 1 !important;
}
/* ── Botão secundário ── */
[data-testid="stButton"] button[kind="secondary"] {
    background: transparent !important;
    color: #f97316 !important;
    border: 1px solid #f97316 !important;
    opacity: 1 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    margin-top: 0 !important;
}
/* ── Divider ── */
hr { border-color: #1a1812 !important; }
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
    caminho = Path(__file__).parent / "perguntas_400.json"
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()

# ── Estado ──────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "tela": "home",
        "areas_selecionadas": list(AREA_CORES.keys()),
        "questoes_ativas": [],
        "indice_atual": 0,
        "respostas": {},
        "mostrar_explicacao": False,
        "historico": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ─────────────────────────────────────────────────────────────────
def iniciar_simulado():
    questoes_por_area = {}
    
    for area in st.session_state.areas_selecionadas:
        qs_area = [q for q in PERGUNTAS if q["area"] == area]
        if len(qs_area) >= 20:
            selecionadas = random.sample(qs_area, 20)
        else:
            selecionadas = qs_area[:]  # usa todas se tiver menos
            if len(qs_area) > 0:
                st.toast(f"Área {area} tem apenas {len(qs_area)} questões disponíveis.", icon="⚠️")
        questoes_por_area[area] = selecionadas
    
    # Junta todas e embaralha
    todas_questoes = []
    for qs in questoes_por_area.values():
        todas_questoes.extend(qs)
    
    random.shuffle(todas_questoes)
    
    st.session_state.questoes_ativas = todas_questoes
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
    res = st.session_state.respostas
    acertos = sum(1 for i, q in enumerate(qs) if res.get(i) == q["correta"])
    total = len(qs)
    pct = round(acertos / total * 100) if total else 0
    st.session_state.historico.append({"acertos": acertos, "total": total, "pct": pct})
    st.session_state.tela = "resultado"

def calcular_por_area():
    qs = st.session_state.questoes_ativas
    res = st.session_state.respostas
    dados = {}
    for area in AREA_CORES:
        area_qs = [(i, q) for i, q in enumerate(qs) if q["area"] == area]
        acertos = sum(1 for i, q in area_qs if res.get(i) == q["correta"])
        total = len(area_qs)
        score = round(acertos / total * 1000) if total else 0
        dados[area] = {"acertos": acertos, "total": total, "score": score}
    return dados

# ══════════════════════════════════════════════════════════════════════════════
# TELA: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.tela == "home":
    st.markdown("<div class='titulo-preparatorio'>Preparatório Oficial</div>", unsafe_allow_html=True)
    st.markdown("<div class='titulo-enem'>ENEM</div>", unsafe_allow_html=True)
    st.markdown("<div class='titulo-simulador'>Simulador</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitulo'>20 questões por área · Embaralhadas · Análise detalhada</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-label'>Selecione as áreas do simulado</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, (area, cor) in enumerate(AREA_CORES.items()):
        sel = area in st.session_state.areas_selecionadas
        icone = AREA_ICONES[area]
        qtd = sum(1 for q in PERGUNTAS if q["area"] == area)
        r2, g2, b2 = int(cor[1:3],16), int(cor[3:5],16), int(cor[5:7],16)
        bg = f"rgba({r2},{g2},{b2},0.18)" if sel else "rgba(255,255,255,0.03)"
        check_bg = cor if sel else "transparent"
        check_bd = cor if sel else "#3a3228"
        check_txt = "✓" if sel else ""
        name_col = cor if sel else "#6a6058"
        border = cor if sel else "#2a2228"

        target_col = col1 if i < 2 else col2
        with target_col:
            st.markdown(
                f"""<div class='area-card' style='border-color:{border}; background:{bg}'>
                    <span class='area-icon'>{icone}</span>
                    <div>
                        <div class='area-name' style='color:{name_col}'>{area}</div>
                        <div class='area-count'>{qtd} questões disponíveis</div>
                    </div>
                    <div class='area-check' style='background:{check_bg}; border:2px solid {check_bd}; color:#0a0a0f; margin-left:auto'>{check_txt}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"{'✓' if sel else '＋'} {area}", key=f"area_{area}", use_container_width=True):
                if sel and len(st.session_state.areas_selecionadas) > 1:
                    st.session_state.areas_selecionadas.remove(area)
                elif not sel:
                    st.session_state.areas_selecionadas.append(area)
                st.rerun()

    total_areas = len(st.session_state.areas_selecionadas)
    total_qs = total_areas * 20
    st.markdown(f"<div class='total-label'>Total aproximado: {total_qs} questões (20 por área)</div>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Iniciar Simulado →", type="primary", use_container_width=True):
            iniciar_simulado()
            st.rerun()

    if st.session_state.historico:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Histórico de simulados</div>", unsafe_allow_html=True)
        for i, h in enumerate(reversed(st.session_state.historico)):
            cor_h = "#10b981" if h["pct"] >= 70 else "#f97316" if h["pct"] >= 50 else "#ef4444"
            st.markdown(
                f"<div class='hist-row'>"
                f"<span>Simulado #{len(st.session_state.historico)-i}</span>"
                f"<span>{h['acertos']}/{h['total']} acertos</span>"
                f"<span style='color:{cor_h};font-weight:700'>{h['pct']}%</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# TELA: QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.tela == "quiz":
    qs = st.session_state.questoes_ativas
    idx = st.session_state.indice_atual
    q = qs[idx]
    total = len(qs)
    cor = AREA_CORES[q["area"]]

    col_p, col_n = st.columns([6, 1])
    with col_p:
        st.progress((idx + 1) / total)
    with col_n:
        st.markdown(
            f"<div style='font-family:Inter,sans-serif;font-size:12px;color:#5a5048;text-align:right;padding-top:5px'>{idx+1}/{total}</div>",
            unsafe_allow_html=True,
        )

    r, g, b = int(cor[1:3],16), int(cor[3:5],16), int(cor[5:7],16)
    st.markdown(
        f"<div style='margin-bottom:16px'>"
        f"<span class='badge' style='background:rgba({r},{g},{b},0.13);color:{cor};border:1px solid rgba({r},{g},{b},0.3)'>{AREA_ICONES[q['area']]} {q['area']}</span>"
        f"<span class='badge' style='background:rgba(255,255,255,0.05);color:#6a6058;border:1px solid #2a2228'>{q['competencia']}</span></div>",
        unsafe_allow_html=True,
    )

    enunciado_html = q["enunciado"].replace("\n", "<br>")
    st.markdown(f"<div class='question-box'>{enunciado_html}</div>", unsafe_allow_html=True)

    respondido = st.session_state.mostrar_explicacao
    resposta_dada = st.session_state.respostas.get(idx)

    for i, alt in enumerate(q["alternativas"]):
        letra = LETRAS[i]
        if respondido:
            if i == q["correta"]:
                css = "alt-correta"
            elif i == resposta_dada and i != q["correta"]:
                css = "alt-errada"
            else:
                css = "alt-neutra"
            st.markdown(
                f"<div class='alt-btn {css}'><strong>{letra})</strong> {alt}</div>",
                unsafe_allow_html=True,
            )
        else:
            if st.button(f"{letra}) {alt}", key=f"alt_{idx}_{i}", use_container_width=True):
                responder(i)
                st.rerun()

    if respondido:
        st.markdown(
            f"<div class='explicacao-box'>"
            f"<div class='explicacao-titulo'>💡 Explicação</div>"
            f"{q['explicacao']}"
            f"</div>",
            unsafe_allow_html=True,
        )
        _, col_btn = st.columns([3, 1])
        with col_btn:
            label = "Próxima →" if idx < total - 1 else "Ver Resultado 🏆"
            if st.button(label, type="primary", use_container_width=True):
                proxima_questao()
                st.rerun()

    with st.expander("⚙️ Opções"):
        if st.button("🏠 Voltar ao início (perde progresso)"):
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
    cor_pct = "#10b981" if pct >= 70 else "#f97316" if pct >= 50 else "#ef4444"
    emoji = "🎯" if pct >= 70 else "📈" if pct >= 50 else "📚"
    msg = "Excelente desempenho!" if pct >= 70 else "Bom, continue praticando!" if pct >= 50 else "Precisa reforçar os estudos."
    r, g, b = int(cor_pct[1:3],16), int(cor_pct[3:5],16), int(cor_pct[5:7],16)

    st.markdown(f"<div class='section-label' style='margin-top:8px'>Resultado Final</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-pct' style='color:{cor_pct};text-shadow:0 0 60px rgba({r},{g},{b},0.25)'>{pct}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-sub'>{acertos} de {total} questões corretas</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center;margin-bottom:32px'>"
        f"<span class='result-badge' style='background:rgba({r},{g},{b},0.12);color:{cor_pct};border:1px solid rgba({r},{g},{b},0.3)'>"
        f"{emoji} {msg}</span></div>",
        unsafe_allow_html=True,
    )

    dados_area = calcular_por_area()
    n = len([a for a in dados_area if dados_area[a]["total"] > 0])
    if n > 0:
        cols = st.columns(n)
        idx_col = 0
        for area, d in dados_area.items():
            if d["total"] == 0:
                continue
            cor = AREA_CORES[area]
            r2, g2, b2 = int(cor[1:3],16), int(cor[3:5],16), int(cor[5:7],16)
            pct_barra = d["score"] / 10
            with cols[idx_col]:
                st.markdown(
                    f"""<div class='score-card' style='border:1px solid rgba({r2},{g2},{b2},0.2)'>
                        <div style='font-size:26px'>{AREA_ICONES[area]}</div>
                        <div class='score-card-area' style='color:{cor}'>{area.split()[0]}</div>
                        <div class='score-card-value' style='color:{cor}'>{d['score']}</div>
                        <div style='height:3px;background:#1a1812;border-radius:2px;margin:6px 0'>
                            <div style='height:100%;background:{cor};border-radius:2px;width:{pct_barra}%'></div>
                        </div>
                        <div class='score-card-acertos'>{d['acertos']}/{d['total']} acertos</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            idx_col += 1

    st.markdown("<br>", unsafe_allow_html=True)

    col_bar, col_radar = st.columns(2)
    areas_com_questoes = [a for a, d in dados_area.items() if d["total"] > 0]
    if areas_com_questoes:
        labels = [a.split()[0] for a in areas_com_questoes]
        scores = [dados_area[a]["score"] for a in areas_com_questoes]
        cores = [AREA_CORES[a] for a in areas_com_questoes]

        with col_bar:
            fig_bar = go.Figure(go.Bar(
                x=labels, y=scores,
                marker_color=cores,
                text=scores, textposition="outside",
                textfont=dict(size=12, color="#8a8070"),
            ))
            fig_bar.update_layout(
                paper_bgcolor="#0f0f18", plot_bgcolor="#0f0f18",
                font_color="#8a8070", height=240,
                yaxis=dict(range=[0, 1150], showgrid=False, zeroline=False, showticklabels=False),
                xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                margin=dict(t=36, b=10, l=10, r=10),
                title=dict(text="Score por área (0–1000)", font=dict(size=11, color="#5a5048"), x=0),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_radar:
            pcts_r = [round(dados_area[a]["acertos"]/dados_area[a]["total"]*100) if dados_area[a]["total"] else 0 for a in areas_com_questoes]
            fig_rad = go.Figure(go.Scatterpolar(
                r=pcts_r + [pcts_r[0]],
                theta=labels + [labels[0]],
                fill="toself",
                fillcolor="rgba(249,115,22,0.12)",
                line=dict(color="#f97316", width=2),
            ))
            fig_rad.update_layout(
                paper_bgcolor="#0f0f18", plot_bgcolor="#0f0f18",
                font_color="#8a8070", height=240,
                polar=dict(
                    bgcolor="#0f0f18",
                    radialaxis=dict(visible=True, range=[0,100], showticklabels=False, gridcolor="#2a2228"),
                    angularaxis=dict(gridcolor="#2a2228", tickfont=dict(size=10)),
                ),
                margin=dict(t=36, b=10, l=20, r=20),
                title=dict(text="Radar de desempenho (%)", font=dict(size=11, color="#5a5048"), x=0),
            )
            st.plotly_chart(fig_rad, use_container_width=True)

    areas_fracas = [a for a, d in dados_area.items() if d["score"] < 600 and d["total"] > 0]
    if areas_fracas:
        st.markdown("<div class='section-label' style='margin-top:8px'>📌 Foque seus estudos</div>", unsafe_allow_html=True)
        for area in areas_fracas:
            cor = AREA_CORES[area]
            st.markdown(
                f"<div class='area-fraca' style='border-color:{cor}'>"
                f"<div class='area-fraca-nome' style='color:{cor}'>{AREA_ICONES[area]} {area}</div>"
                f"<div class='area-fraca-desc'>Score abaixo de 600. Revise os fundamentos e pratique mais questões desta área.</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>🔍 Revisão de questões</div>", unsafe_allow_html=True)

    for i, q in enumerate(qs):
        acertou = respostas.get(i) == q["correta"]
        icone_q = "✅" if acertou else "❌"
        with st.expander(f"{icone_q} Q{i+1} · {q['area']} — {q['competencia']}"):
            st.markdown(f"<div style='font-family:EB Garamond,serif;font-size:16px;line-height:1.7;color:#d0c8b8;white-space:pre-line'>{q['enunciado']}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for j, alt in enumerate(q["alternativas"]):
                letra = LETRAS[j]
                if j == q["correta"]:
                    st.markdown(f"<div class='alt-btn alt-correta'>✅ <strong>{letra})</strong> {alt}</div>", unsafe_allow_html=True)
                elif j == respostas.get(i) and j != q["correta"]:
                    st.markdown(f"<div class='alt-btn alt-errada'>❌ <strong>{letra})</strong> {alt} <em style='opacity:0.6'>← sua resposta</em></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='alt-btn alt-neutra'><strong>{letra})</strong> {alt}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='explicacao-box'><div class='explicacao-titulo'>💡 Explicação</div>{q['explicacao']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↺ Novo simulado", use_container_width=True, type="secondary"):
            iniciar_simulado()
            st.rerun()
    with col2:
        if st.button("🏠 Início", use_container_width=True, type="primary"):
            st.session_state.tela = "home"
            st.rerun()
