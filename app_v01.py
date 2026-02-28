import streamlit as st
import json
import random

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="ENEM Simulador", layout="wide")

# ---------------------------------------------------
# CARREGAR QUESTÕES
# ---------------------------------------------------
@st.cache_data
def carregar_questoes():
    with open("perguntas_400.json", "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_questoes()

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "areas" not in st.session_state:
    st.session_state.areas = []

if "tela" not in st.session_state:
    st.session_state.tela = "inicio"

if "questoes" not in st.session_state:
    st.session_state.questoes = []

if "indice" not in st.session_state:
    st.session_state.indice = 0

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

# ---------------------------------------------------
# FUNÇÃO INICIAR SIMULADO
# ---------------------------------------------------
def iniciar_simulado():

    questoes_final = []

    for area in st.session_state.areas:
        qs_area = [q for q in PERGUNTAS if q["area"] == area]
        random.shuffle(qs_area)
        questoes_final.extend(qs_area[:10])

    random.shuffle(questoes_final)

    st.session_state.questoes = questoes_final
    st.session_state.indice = 0
    st.session_state.respostas = {}
    st.session_state.tela = "quiz"

# ---------------------------------------------------
# TELA INICIAL
# ---------------------------------------------------
if st.session_state.tela == "inicio":

    st.title("SELECIONE AS ÁREAS DO SIMULADO")

    col1, col2 = st.columns(2)

    def toggle(area):
        if area in st.session_state.areas:
            st.session_state.areas.remove(area)
        else:
            st.session_state.areas.append(area)

    with col1:
        st.button("✓ Linguagens" if "Linguagens" in st.session_state.areas else "Linguagens",
                  on_click=toggle, args=("Linguagens",))
        st.button("✓ Ciências Humanas" if "Ciências Humanas" in st.session_state.areas else "Ciências Humanas",
                  on_click=toggle, args=("Ciências Humanas",))

    with col2:
        st.button("✓ Ciências da Natureza" if "Ciências da Natureza" in st.session_state.areas else "Ciências da Natureza",
                  on_click=toggle, args=("Ciências da Natureza",))
        st.button("✓ Matemática" if "Matemática" in st.session_state.areas else "Matemática",
                  on_click=toggle, args=("Matemática",))

    total = len(st.session_state.areas) * 10
    st.write(f"{total} questões selecionadas")

    if st.button("INICIAR SIMULADO →"):
        if len(st.session_state.areas) == 0:
            st.warning("Selecione pelo menos uma área.")
        else:
            iniciar_simulado()

# ---------------------------------------------------
# TELA QUIZ
# ---------------------------------------------------
elif st.session_state.tela == "quiz":

    questoes = st.session_state.questoes
    indice = st.session_state.indice

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
                st.session_state.indice += 1
                st.rerun()

        with col2:
            if st.button("Finalizar Simulado"):
                st.session_state.tela = "resultado"
                st.rerun()

    else:
        st.session_state.tela = "resultado"
        st.rerun()

# ---------------------------------------------------
# RESULTADO
# ---------------------------------------------------
elif st.session_state.tela == "resultado":

    st.title("Resultado Final")

    total = len(st.session_state.questoes)
    acertos = 0

    for i, q in enumerate(st.session_state.questoes):
        if i in st.session_state.respostas:
            if st.session_state.respostas[i] == q["correta"]:
                acertos += 1

    percentual = (acertos / total) * 100

    st.metric("Acertos", f"{acertos}/{total}")
    st.metric("Percentual", f"{percentual:.1f}%")

    if st.button("Novo Simulado"):
        st.session_state.tela = "inicio"
        st.session_state.areas = []
        st.rerun()
