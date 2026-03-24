import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_acesso(
    nome: str,
    user_agent: str = "",
    duracao_segundos: int = 0,
    celular: str = "",
    email: str = "",
    idade: str = "",
    sexo: str = ""
):
    data = {
        "nome_completo": nome.strip(),
        "celular":       celular.strip(),
        "email":         email.strip(),
        "idade":         int(idade) if idade else None,
        "sexo":          sexo,
    }
    response = supabase.table("tbl_aluno_enem").insert(data).execute()
    return response
