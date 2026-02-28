import streamlit as st
import json
import random
import plotly.express as px

# ---------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------
st.set_page_config(page_title="Simulado ENEM", page_icon="📘", layout="wide")

# ---------------------------------------------------
# CARREGAR BANCO DE QUESTÕES
# ---------------------------------------------------
@st.cache_data
def carregar_questoes():
    with open("perguntas_400.json", "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_questoes()

AREAS = list(set(q["area"] for q in PERGUNTAS))

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

if "questoes_ativas" not in st.session_state:
    st.session_state.questoes_ativas = []

if "indice_atual" not in st.session_state:
    st.session_state.indice_atual = 0

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

if "areas_selecionadas" not in st.session_state:
    st.session_state.areas_selecionadas = []

# ---------------------------------------------------
# FUNÇÃO INICIAR SIMULADO
# ---------------------------------------------------
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

# ---------------------------------------------------
# TELA INICIAL
# ---------------------------------------------------
if st.session_state.tela == "inicio":

    st.title("📘 Simulado ENEM Inteligente")

    st.subheader("Selecione as áreas desejadas:")

    areas = st.multiselect(
        "Áreas",
        AREAS
    )

    if st.button("🚀 Iniciar Simulado"):

        if len(areas) == 0:
            st.warning("Selecione pelo menos uma área.")
        else:
            st.session_state.areas_selecionadas = areas
            iniciar_simulado()

# ---------------------------------------------------
# TELA QUIZ
# ---------------------------------------------------
elif st.session_state.tela == "quiz":

    questoes = st.session_state.questoes_ativas
    indice = st.session_state.indice_atual

    if indice < len(questoes):

        q = questoes[indice]

        st.subheader(f"Questão {indice+1} de {len(questoes)}")
        st.markdown(f"**Área:** {q['area']} | **Dificuldade:** {q['dificuldade']}")
        st.write(q["enunciado"])

        resposta = st.radio(
            "Escolha a alternativa:",
            q["alternativas"],
            key=f"q_{indice}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Próxima ➡️"):
                st.session_state.respostas[indice] = q["alternativas"].index(resposta)
                st.session_state.indice_atual += 1

        with col2:
            if st.button("Finalizar Simulado"):
                st.session_state.respostas[indice] = q["alternativas"].index(resposta)
                st.session_state.tela = "resultado"

    else:
        st.session_state.tela = "resultado"

# ---------------------------------------------------
# TELA RESULTADO
# ---------------------------------------------------
elif st.session_state.tela == "resultado":

    st.title("📊 Resultado Final")

    questoes = st.session_state.questoes_ativas
    respostas = st.session_state.respostas

    total = len(questoes)
    acertos = 0

    resultado_area = {}

    for i, q in enumerate(questoes):

        if q["area"] not in resultado_area:
            resultado_area[q["area"]] = {"acertos": 0, "total": 0}

        resultado_area[q["area"]]["total"] += 1

        if i in respostas and respostas[i] == q["correta"]:
            acertos += 1
            resultado_area[q["area"]]["acertos"] += 1

    percentual = (acertos / total) * 100

    st.metric("Total de Acertos", f"{acertos}/{total}")
    st.metric("Percentual", f"{percentual:.1f}%")

    # -------------------------------
    # Gráfico por área
    # -------------------------------
    dados_grafico = []

    for area, dados in resultado_area.items():
        perc = (dados["acertos"] / dados["total"]) * 100
        dados_grafico.append({
            "Área": area,
            "Percentual de Acertos": perc
        })

    fig = px.bar(
        dados_grafico,
        x="Área",
        y="Percentual de Acertos",
        title="Desempenho por Área"
    )

    st.plotly_chart(fig, use_container_width=True)

    if st.button("🔄 Novo Simulado"):
        st.session_state.tela = "inicio"
