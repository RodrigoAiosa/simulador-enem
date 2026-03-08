import streamlit as st
import json
import random
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import io
import re

from registrar_acesso import registrar_acesso


# ── Configuração da página ─────────────────────────────
st.set_page_config(
    page_title="Simulador ENEM",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ── Constantes ─────────────────────────────────────────
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

LETRAS = ["A","B","C","D","E"]


# ── Carregar perguntas ─────────────────────────────────
@st.cache_data
def carregar_perguntas():
    caminho = Path(__file__).parent / "perguntas_400.json"
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

PERGUNTAS = carregar_perguntas()


# ── Estado da sessão ───────────────────────────────────
def init_state():

    defaults = {
        "tela":"form",
        "nome_aluno":"",
        "celular":"",
        "email":"",
        "idade":"",
        "sexo":"Não informar",

        "areas_selecionadas":list(AREA_CORES.keys()),

        "questoes_ativas":[],
        "indice_atual":0,
        "respostas":{},
        "mostrar_explicacao":False,

        "tempo_inicio":None,
        "user_agent":"",
        "historico":[]
    }

    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Iniciar simulado ───────────────────────────────────
def iniciar_simulado():

    qs=[]

    for area in st.session_state.areas_selecionadas:

        area_qs=[q for q in PERGUNTAS if q["area"]==area]

        random.shuffle(area_qs)

        qs.extend(area_qs[:20])

    random.shuffle(qs)

    st.session_state.questoes_ativas=qs
    st.session_state.indice_atual=0
    st.session_state.respostas={}
    st.session_state.mostrar_explicacao=False
    st.session_state.tempo_inicio=datetime.now()

    st.session_state.tela="quiz"


# ── Finalizar simulado ─────────────────────────────────
def finalizar():

    qs=st.session_state.questoes_ativas
    res=st.session_state.respostas

    acertos=sum(
        1 for i,q in enumerate(qs)
        if res.get(i)==q["correta"]
    )

    total=len(qs)
    pct=round(acertos/total*100)

    duracao=int((datetime.now()-st.session_state.tempo_inicio).total_seconds())

    registrar_acesso(
        nome=st.session_state.nome_aluno,
        celular=st.session_state.celular,
        email=st.session_state.email,
        idade=st.session_state.idade,
        sexo=st.session_state.sexo,
        user_agent=st.session_state.user_agent,
        duracao_segundos=duracao
    )

    st.session_state.historico.append(
        {"acertos":acertos,"total":total,"pct":pct}
    )

    st.session_state.tela="resultado"


# ═══════════════════════════════════════════════════════
# FORMULÁRIO
# ═══════════════════════════════════════════════════════

if st.session_state.tela=="form":

    st.title("🎓 Simulador ENEM")

    st.subheader("Informe seus dados")

    st.session_state.nome_aluno = st.text_input(
        "Nome",
        value=st.session_state.nome_aluno
    )

    st.session_state.celular = st.text_input(
        "Celular",
        help="Digite somente números"
    )

    st.session_state.email = st.text_input("Email")

    st.session_state.idade = st.text_input("Idade")

    st.session_state.sexo = st.selectbox(
        "Sexo",
        ["Masculino","Feminino","Não informar"]
    )


    # ── Regex validação ─────────────────────────────

    nome_valido = len(st.session_state.nome_aluno.strip())>0

    celular_valido = re.fullmatch(r"\d{10,11}", st.session_state.celular)

    email_valido = re.fullmatch(
        r"[^@]+@[^@]+\.[^@]+",
        st.session_state.email
    )

    idade_valida = re.fullmatch(r"\d{1,3}", st.session_state.idade)


    if st.session_state.celular and not celular_valido:
        st.error("Celular deve conter apenas números (10 ou 11 dígitos)")

    if st.session_state.email and not email_valido:
        st.error("Email inválido")

    if st.session_state.idade and not idade_valida:
        st.error("Idade deve conter apenas números")


    form_ok = all([
        nome_valido,
        celular_valido,
        email_valido,
        idade_valida
    ])


    if st.button(
        "Iniciar Simulador",
        disabled=not form_ok,
        type="primary"
    ):

        st.session_state.user_agent = st.query_params.get("ua","")
        st.session_state.tela="home"
        st.rerun()



# ═══════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════

elif st.session_state.tela=="home":

    st.title("Selecione as áreas")

    for area in AREA_CORES:

        sel = area in st.session_state.areas_selecionadas

        if st.checkbox(area,value=sel):

            if area not in st.session_state.areas_selecionadas:
                st.session_state.areas_selecionadas.append(area)

        else:

            if area in st.session_state.areas_selecionadas:
                st.session_state.areas_selecionadas.remove(area)


    if st.button("Começar Simulado"):
        iniciar_simulado()
        st.rerun()


# ═══════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════

elif st.session_state.tela=="quiz":

    qs = st.session_state.questoes_ativas
    idx = st.session_state.indice_atual

    q = qs[idx]

    st.subheader(f"Questão {idx+1}/{len(qs)}")

    st.write(q["enunciado"])


    for i,alt in enumerate(q["alternativas"]):

        if st.button(f"{LETRAS[i]}) {alt}"):

            st.session_state.respostas[idx]=i

            if idx < len(qs)-1:

                st.session_state.indice_atual+=1
                st.rerun()

            else:

                finalizar()
                st.rerun()



# ═══════════════════════════════════════════════════════
# RESULTADO
# ═══════════════════════════════════════════════════════

elif st.session_state.tela=="resultado":

    qs = st.session_state.questoes_ativas
    res = st.session_state.respostas

    acertos=sum(
        1 for i,q in enumerate(qs)
        if res.get(i)==q["correta"]
    )

    total=len(qs)

    pct=round(acertos/total*100)

    st.title("Resultado")

    st.metric(
        "Pontuação",
        f"{pct}%"
    )

    st.write(f"{acertos} de {total} acertos")


    if st.button("Novo Simulado"):
        iniciar_simulado()
        st.rerun()
