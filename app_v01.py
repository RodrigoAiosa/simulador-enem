import streamlit as st
import json
import random
from pathlib import Path

# ---------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------
st.set_page_config(
    page_title="Simulador ENEM",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------
# CARREGAR PERGUNTAS
# ---------------------------------------
@st.cache_data
def carregar_perguntas():
    caminho = Path(__file__).parent / "perguntas_400.json"
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()

# ---------------------------------------
# ESTADO INICIAL
# ---------------------------------------
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

if "mostrar_explicacao" not in st.session_state:
    st.session_state.mostrar_explicacao = False


# ---------------------------------------
# FUNÇÃO PARA INICIAR SIMULADO
# ---------------------------------------
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
    st.session_state.mostrar_explicacao = False
    st.session_state.tela = "quiz"


# ---------------------------------------
# TELA INICIAL
# ---------------------------------------
if st.session_state.tela == "inicio":

    st.title("🎓 Simulador ENEM Inteligente")

    st.subheader("Selecione as áreas para o simulado:")

    areas_disponiveis = list(set(q["area"] for q in PERGUNTAS))

    selecionadas = st.multiselect(
        "Áreas:",
        areas_disponiveis
    )

    if st.button("🚀 Iniciar Simulado"):
        if not selecionadas:
            st.warning("Selecione pelo menos uma área.")
        else:
            st.session_state.areas_selecionadas = selecionadas
            iniciar_simulado()


# ---------------------------------------
# TELA DO QUIZ
# ---------------------------------------
elif st.session_state.tela == "quiz":

    total = len(st.session_state.questoes_ativas)
    indice = st.session_state.indice_atual

    if indice < total:

        questao = st.session_state.questoes_ativas[indice]

        st.progress((indice + 1) / total)

        st.subheader(f"Questão {indice + 1} de {total}")
        st.markdown(f"**Área:** {questao['area']}")
        st.markdown(f"**Dificuldade:** {questao['dificuldade']}")
        st.markdown("---")
        st.write(questao["enunciado"])

        resposta = st.radio(
            "Escolha uma alternativa:",
            questao["alternativas"],
            key=f"radio_{indice}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Responder"):
                st.session_state.respostas[indice] = questao["alternativas"].index(resposta)
                st.session_state.mostrar_explicacao = True

        with col2:
            if st.button("Próxima"):
                if indice not in st.session_state.respostas:
                    st.warning("Responda antes de avançar.")
                else:
                    st.session_state.indice_atual += 1
                    st.session_state.mostrar_explicacao = False
                    st.rerun()

        # Mostrar explicação
        if st.session_state.mostrar_explicacao:
            correta = questao["correta"]
            usuario = st.session_state.respostas[indice]

            if usuario == correta:
                st.success("✅ Resposta correta!")
            else:
                st.error(f"❌ Resposta incorreta. Correta: {questao['alternativas'][correta]}")

            st.info(f"📘 Explicação: {questao['explicacao']}")

    else:
        st.session_state.tela = "resultado"
        st.rerun()


# ---------------------------------------
# TELA RESULTADO
# ---------------------------------------
elif st.session_state.tela == "resultado":

    st.title("📊 Resultado Final")

    total = len(st.session_state.questoes_ativas)
    acertos = 0

    for i, questao in enumerate(st.session_state.questoes_ativas):
        if i in st.session_state.respostas:
            if st.session_state.respostas[i] == questao["correta"]:
                acertos += 1

    percentual = (acertos / total) * 100

    st.metric("Total de Questões", total)
    st.metric("Acertos", acertos)
    st.metric("Percentual", f"{percentual:.1f}%")

    if percentual >= 70:
        st.success("🔥 Excelente desempenho!")
    elif percentual >= 40:
        st.warning("⚠️ Bom, mas pode melhorar.")
    else:
        st.error("📚 Continue estudando, você consegue!")

    if st.button("🔁 Novo Simulado"):
        st.session_state.tela = "inicio"
        st.session_state.indice_atual = 0
        st.session_state.respostas = {}
        st.session_state.questoes_ativas = []
        st.rerun()
