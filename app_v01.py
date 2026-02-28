import streamlit as st
import json
import random
from collections import Counter

# ----------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------------
st.set_page_config(
    page_title="Simulado ENEM",
    page_icon="📚",
    layout="wide"
)

# ----------------------------------
# CARREGAR PERGUNTAS
# ----------------------------------
@st.cache_data
def carregar_perguntas():
    with open("perguntas_400.json", "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()

# ----------------------------------
# ESTADO INICIAL
# ----------------------------------
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

if "areas_selecionadas" not in st.session_state:
    st.session_state.areas_selecionadas = []

if "questoes_ativas" not in st.session_state:
    st.session_state.questoes_ativas = []

if "indice_atual" not in st.session_state:
    st.session_state.indice_atual = 0

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

# ----------------------------------
# FUNÇÃO INICIAR SIMULADO
# ----------------------------------
def iniciar_simulado():
    questoes_final = []

    for area in st.session_state.areas_selecionadas:
        qs_area = [q for q in PERGUNTAS if q["area"] == area]
        random.shuffle(qs_area)
        questoes_final.extend(qs_area[:10])  # 10 por área

    random.shuffle(questoes_final)

    st.session_state.questoes_ativas = questoes_final
    st.session_state.indice_atual = 0
    st.session_state.respostas = {}
    st.session_state.tela = "quiz"

# ----------------------------------
# TELA INICIAL
# ----------------------------------
if st.session_state.tela == "inicio":

    st.title("📚 Simulado ENEM Inteligente")

    areas = list(set(q["area"] for q in PERGUNTAS))
    selecionadas = st.multiselect(
        "Selecione as áreas:",
        areas
    )

    st.session_state.areas_selecionadas = selecionadas

    if st.button("🚀 Iniciar Simulado"):
        if len(selecionadas) == 0:
            st.warning("Selecione pelo menos uma área.")
        else:
            iniciar_simulado()

# ----------------------------------
# TELA QUIZ
# ----------------------------------
elif st.session_state.tela == "quiz":

    total = len(st.session_state.questoes_ativas)
    indice = st.session_state.indice_atual
    questao = st.session_state.questoes_ativas[indice]

    st.progress((indice + 1) / total)

    st.subheader(f"Questão {indice + 1} de {total}")
    st.markdown(f"**Área:** {questao['area']}")
    st.markdown(questao["pergunta"])

    alternativa = st.radio(
        "Escolha uma alternativa:",
        questao["alternativas"],
        key=f"radio_{indice}"
    )

    if st.button("Salvar Resposta"):
        st.session_state.respostas[indice] = alternativa

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Anterior") and indice > 0:
            st.session_state.indice_atual -= 1

    with col2:
        if st.button("➡️ Próxima"):
            if indice < total - 1:
                st.session_state.indice_atual += 1
            else:
                st.session_state.tela = "resultado"

# ----------------------------------
# TELA RESULTADO
# ----------------------------------
elif st.session_state.tela == "resultado":

    st.title("📊 Resultado Final")

    acertos = 0
    total = len(st.session_state.questoes_ativas)
    desempenho_area = Counter()

    for i, questao in enumerate(st.session_state.questoes_ativas):
        resposta_usuario = st.session_state.respostas.get(i)
        if resposta_usuario == questao["resposta"]:
            acertos += 1
            desempenho_area[questao["area"]] += 1

    porcentagem = (acertos / total) * 100

    st.metric("Total de Acertos", f"{acertos} / {total}")
    st.metric("Aproveitamento", f"{porcentagem:.1f}%")

    st.subheader("📈 Desempenho por Área")
    st.bar_chart(desempenho_area)

    if st.button("🔄 Refazer Simulado"):
        st.session_state.tela = "inicio"
