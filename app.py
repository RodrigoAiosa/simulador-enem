import streamlit as st
import json
import random
import time
import re

from registrar_acesso import registrar_acesso


# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Simulador ENEM",
    layout="centered"
)


# ═══════════════════════════════════════════════════════════════
# CARREGAR QUESTÕES
# ═══════════════════════════════════════════════════════════════

with open("questoes.json", "r", encoding="utf-8") as f:
    QUESTOES = json.load(f)


# ═══════════════════════════════════════════════════════════════
# ÁREAS
# ═══════════════════════════════════════════════════════════════

AREA_CORES = {
    "Matemática": "#ff4b4b",
    "Linguagens": "#ffa500",
    "Humanas": "#2ecc71",
    "Natureza": "#3498db",
}


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_state():

    defaults = {
        "tela": "nome",

        "nome_aluno": "",
        "celular": "",
        "email": "",
        "idade": "",
        "sexo": "Não informar",

        "areas_selecionadas": list(AREA_CORES.keys()),
        "questoes_ativas": [],
        "indice_atual": 0,
        "respostas": {},
        "mostrar_explicacao": False,

        "historico": [],

        "tempo_inicio": None,
        "tempo_decorrido": 0,

        "user_agent": "",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ═══════════════════════════════════════════════════════════════
# FUNÇÕES
# ═══════════════════════════════════════════════════════════════

def iniciar_simulado():

    questoes_filtradas = [
        q for q in QUESTOES
        if q["area"] in st.session_state.areas_selecionadas
    ]

    random.shuffle(questoes_filtradas)

    st.session_state.questoes_ativas = questoes_filtradas[:10]
    st.session_state.indice_atual = 0
    st.session_state.respostas = {}
    st.session_state.mostrar_explicacao = False

    st.session_state.tempo_inicio = time.time()

    st.session_state.tela = "questao"
    st.rerun()


def finalizar():

    duracao = int(time.time() - st.session_state.tempo_inicio)

    registrar_acesso(
        nome=st.session_state.nome_aluno,
        celular=st.session_state.celular,
        email=st.session_state.email,
        idade=st.session_state.idade,
        sexo=st.session_state.sexo,
        user_agent=st.session_state.get("user_agent", ""),
        duracao_segundos=duracao
    )

    st.session_state.tempo_decorrido = duracao
    st.session_state.tela = "resultado"

    st.rerun()


# ═══════════════════════════════════════════════════════════════
# TELA: NOME
# ═══════════════════════════════════════════════════════════════

if st.session_state.tela == "nome":

    st.markdown("## Simulador ENEM")

    st.session_state.nome_aluno = st.text_input(
        "Nome",
        value=st.session_state.nome_aluno
    )

    st.session_state.celular = st.text_input(
        "Celular (somente números)",
        value=st.session_state.celular
    )

    st.session_state.email = st.text_input(
        "Email",
        value=st.session_state.email
    )

    st.session_state.idade = st.text_input(
        "Idade",
        value=st.session_state.idade
    )

    st.session_state.sexo = st.selectbox(
        "Sexo",
        ["Masculino", "Feminino", "Não informar"],
        index=["Masculino","Feminino","Não informar"].index(st.session_state.sexo)
    )

    # ═══════════════════════════════════════
    # VALIDAÇÕES
    # ═══════════════════════════════════════

    nome_ok = len(st.session_state.nome_aluno.strip()) > 0

    celular_ok = re.fullmatch(r"\d{10,11}", st.session_state.celular)
    email_ok = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", st.session_state.email)
    idade_ok = re.fullmatch(r"\d{1,3}", st.session_state.idade)

    if st.session_state.celular and not celular_ok:
        st.error("Celular inválido")

    if st.session_state.email and not email_ok:
        st.error("Email inválido")

    if st.session_state.idade and not idade_ok:
        st.error("Idade inválida")

    form_ok = all([
        nome_ok,
        celular_ok,
        email_ok,
        idade_ok
    ])

    if st.button(
        "Avançar",
        disabled=not form_ok
    ):

        st.session_state.tela = "home"
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# TELA: HOME
# ═══════════════════════════════════════════════════════════════

elif st.session_state.tela == "home":

    st.markdown(f"### Olá, {st.session_state.nome_aluno}")

    st.write("Escolha as áreas do simulado")

    selecionadas = []

    for area in AREA_CORES:

        if st.checkbox(area, value=True):
            selecionadas.append(area)

    st.session_state.areas_selecionadas = selecionadas

    if st.button("Iniciar Simulado"):

        iniciar_simulado()


# ═══════════════════════════════════════════════════════════════
# TELA: QUESTÃO
# ═══════════════════════════════════════════════════════════════

elif st.session_state.tela == "questao":

    indice = st.session_state.indice_atual
    questao = st.session_state.questoes_ativas[indice]

    st.markdown(f"### Questão {indice+1}")

    st.write(questao["pergunta"])

    resposta = st.radio(
        "Escolha:",
        questao["alternativas"],
        key=f"q{indice}"
    )

    if st.button("Responder"):

        st.session_state.respostas[indice] = resposta

        if indice + 1 >= len(st.session_state.questoes_ativas):

            finalizar()

        else:

            st.session_state.indice_atual += 1
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# TELA: RESULTADO
# ═══════════════════════════════════════════════════════════════

elif st.session_state.tela == "resultado":

    acertos = 0

    for i, q in enumerate(st.session_state.questoes_ativas):

        if st.session_state.respostas.get(i) == q["resposta"]:
            acertos += 1

    st.markdown("## Resultado")

    st.write(f"Acertos: {acertos}")
    st.write(f"Tempo: {st.session_state.tempo_decorrido} segundos")

    if st.button("Refazer"):

        st.session_state.tela = "home"
        st.rerun()
