import streamlit as st
import json
import random

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Simulado ENEM",
    page_icon="📘",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def carregar_perguntas():
    with open("perguntas_400.json", "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()

AREA_CORES = {
    "Linguagens": "#E53935",
    "Matemática": "#1E88E5",
    "Ciências Humanas": "#8E24AA",
    "Ciências da Natureza": "#43A047"
}

AREA_ICONES = {
    "Linguagens": "📝",
    "Matemática": "📐",
    "Ciências Humanas": "🌎",
    "Ciências da Natureza": "🔬"
}

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "areas_selecionadas" not in st.session_state:
    st.session_state.areas_selecionadas = list(AREA_CORES.keys())

if "quantidade" not in st.session_state:
    st.session_state.quantidade = 10

if "simulado_iniciado" not in st.session_state:
    st.session_state.simulado_iniciado = False

if "questoes_sorteadas" not in st.session_state:
    st.session_state.questoes_sorteadas = []

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

# --------------------------------------------------
# HOME
# --------------------------------------------------
if not st.session_state.simulado_iniciado:

    st.title("📘 Simulado ENEM Inteligente")

    st.subheader("Selecione as áreas:")

    cols = st.columns(4)

    for i, area in enumerate(AREA_CORES.keys()):
        with cols[i]:
            selecionado = area in st.session_state.areas_selecionadas
            if st.checkbox(area, value=selecionado):
                if area not in st.session_state.areas_selecionadas:
                    st.session_state.areas_selecionadas.append(area)
            else:
                if area in st.session_state.areas_selecionadas:
                    if len(st.session_state.areas_selecionadas) > 1:
                        st.session_state.areas_selecionadas.remove(area)

    st.divider()

    st.subheader("Quantidade de questões")
    st.session_state.quantidade = st.slider(
        "Escolha a quantidade",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )

    st.divider()

    if st.button("🚀 Iniciar Simulado", use_container_width=True):

        banco_filtrado = [
            q for q in PERGUNTAS
            if q["area"] in st.session_state.areas_selecionadas
        ]

        st.session_state.questoes_sorteadas = random.sample(
            banco_filtrado,
            st.session_state.quantidade
        )

        st.session_state.respostas = {}
        st.session_state.simulado_iniciado = True
        st.rerun()

# --------------------------------------------------
# SIMULADO
# --------------------------------------------------
else:

    st.title("🧠 Simulado em andamento")

    for i, questao in enumerate(st.session_state.questoes_sorteadas):

        st.markdown(f"### Questão {i+1}")
        st.write(questao["pergunta"])

        alternativa = st.radio(
            "Escolha uma alternativa:",
            questao["alternativas"],
            key=f"q_{i}"
        )

        st.session_state.respostas[i] = alternativa
        st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Finalizar Simulado", use_container_width=True):

            acertos = 0

            for i, questao in enumerate(st.session_state.questoes_sorteadas):
                if st.session_state.respostas.get(i) == questao["resposta_correta"]:
                    acertos += 1

            percentual = (acertos / len(st.session_state.questoes_sorteadas)) * 100

            st.success(f"Você acertou {acertos} de {len(st.session_state.questoes_sorteadas)} questões.")
            st.info(f"Aproveitamento: {percentual:.1f}%")

    with col2:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.simulado_iniciado = False
            st.session_state.questoes_sorteadas = []
            st.session_state.respostas = {}
            st.rerun()
