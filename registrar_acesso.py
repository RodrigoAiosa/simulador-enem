import streamlit as st
from supabase import create_client

def registrar_acesso(
    nome: str,
    user_agent: str = "",
    duracao_segundos: int = 0,
    celular: str = "",
    email: str = "",
    idade: str = "",
    sexo: str = "",
    acertos: int = 0,
    total_questoes: int = 0,
    percentual: int = 0,
):
    # ← cliente criado DENTRO da função, evita erro na inicialização
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

    data = {
        "nome_completo":    nome.strip(),
        "celular":          celular.strip() or None,
        "email":            email.strip() or None,
        "idade":            int(idade) if idade else None,
        "sexo":             sexo or None,
        "duracao_segundos": duracao_segundos,
        "acertos":          acertos,
        "total_questoes":   total_questoes,
        "percentual":       percentual,
    }
    try:
        response = supabase.table("tbl_aluno_enem").insert(data).execute()
        return response
    except Exception as e:
        st.warning(f"⚠️ Erro ao salvar: {e}")
        return None
