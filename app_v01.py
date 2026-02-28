import streamlit as st
import json
import random

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="ENEM Simulador",
    page_icon="📘",
    layout="wide"
)

# ---------------------------------------------------
# CSS PREMIUM
# ---------------------------------------------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    background-color: #0b1120;
}

.main {
    background-color: #0b1120;
}

header, footer, #MainMenu {
    visibility: hidden;
}

/* Título principal */
.titulo-enem {
    text-align: center;
    font-size: 70px;
    font-weight: 800;
    color: #f5f5f5;
    letter-spacing: 3px;
    margin-bottom: -20px;
}

.subtitulo {
    text-align: center;
    font-size: 32px;
    color: #ff7a00;
    font-style: italic;
    margin-bottom: 20px;
}

.descricao {
    text-align: center;
    color: #aaa;
    margin-bottom: 50px;
}

/* Cards */
.card {
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 20px;
    transition: 0.3s;
    border: 2px solid;
}

.card:hover {
    transform: scale(1.02);
}

/* Botão principal */
.botao-principal button {
    background-color: #ff7a00 !important;
    color: white !important;
    font-size: 18px !important;
    border-radius: 12px !important;
    padding: 12px 30px !important;
    box-shadow: 0px 0px 20px rgba(255,122,0,0.6);
}

/* Centralizar botão */
.center-button {
    display: flex;
    justify-content: center;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "areas" not in st.session_state:
    st.session_state.areas = []

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown('<div class="titulo-enem">ENEM</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Simulador</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="descricao">40 questões · 4 áreas · Análise por competência · Shuffled</div>',
    unsafe_allow_html=True
)

st.markdown("### ")
st.markdown("## SELECIONE AS ÁREAS DO SIMULADO")

col1, col2 = st.columns(2)

# ---------------------------------------------------
# FUNÇÃO TOGGLE
# ---------------------------------------------------
def toggle_area(area):
    if area in st.session_state.areas:
        st.session_state.areas.remove(area)
    else:
        st.session_state.areas.append(area)

# ---------------------------------------------------
# CARDS
# ---------------------------------------------------

with col1:
    st.markdown(
        """
        <div class="card" style="border-color:#ff7a00; background: rgba(255,122,0,0.05);">
        <h3 style="color:#ff7a00;">✍️ Linguagens</h3>
        <p style="color:#aaa;">10 questões</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("✓ LINGUAGENS" if "Linguagens" in st.session_state.areas else "LINGUAGENS",
              on_click=toggle_area,
              args=("Linguagens",))

with col2:
    st.markdown(
        """
        <div class="card" style="border-color:#00e0a4; background: rgba(0,224,164,0.05);">
        <h3 style="color:#00e0a4;">🔬 Ciências da Natureza</h3>
        <p style="color:#aaa;">10 questões</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("✓ CIÊNCIAS DA NATUREZA" if "Ciências da Natureza" in st.session_state.areas else "CIÊNCIAS DA NATUREZA",
              on_click=toggle_area,
              args=("Ciências da Natureza",))

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        """
        <div class="card" style="border-color:#a855f7; background: rgba(168,85,247,0.05);">
        <h3 style="color:#a855f7;">🏛 Ciências Humanas</h3>
        <p style="color:#aaa;">10 questões</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("✓ CIÊNCIAS HUMANAS" if "Ciências Humanas" in st.session_state.areas else "CIÊNCIAS HUMANAS",
              on_click=toggle_area,
              args=("Ciências Humanas",))

with col4:
    st.markdown(
        """
        <div class="card" style="border-color:#3b82f6; background: rgba(59,130,246,0.05);">
        <h3 style="color:#3b82f6;">📐 Matemática</h3>
        <p style="color:#aaa;">10 questões</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("✓ MATEMÁTICA" if "Matemática" in st.session_state.areas else "MATEMÁTICA",
              on_click=toggle_area,
              args=("Matemática",))

# ---------------------------------------------------
# CONTADOR
# ---------------------------------------------------
total = len(st.session_state.areas) * 10
st.markdown(
    f"<div style='text-align:center; color:#888; margin-top:20px;'>{total} questões selecionadas</div>",
    unsafe_allow_html=True
)

# ---------------------------------------------------
# BOTÃO INICIAR
# ---------------------------------------------------
st.markdown('<div class="center-button botao-principal">', unsafe_allow_html=True)

if st.button("INICIAR SIMULADO →"):
    if len(st.session_state.areas) == 0:
        st.warning("Selecione pelo menos uma área.")
    else:
        st.success("Simulado iniciado! (Aqui você conecta com a tela do quiz)")

st.markdown("</div>", unsafe_allow_html=True)
