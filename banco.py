"""Acesso ao Supabase: cadastro de alunos e telemetria de acessos.

Tabelas usadas (projeto BD_SIMULADOR_ENEM):
- tbl_cadastro           -> um registro por aluno; o e-mail identifica o aluno
- tbl_telemetria_acesso  -> um registro por evento de acesso
"""
import ipaddress
import logging
import re

import streamlit as st
from supabase import create_client

log = logging.getLogger(__name__)

TBL_CADASTRO = "tbl_cadastro"
TBL_TELEMETRIA = "tbl_telemetria_acesso"


@st.cache_resource
def _cliente():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def normalizar_email(email: str) -> str:
    return (email or "").strip().lower()


# ── Cadastro ────────────────────────────────────────────────────────────────
def buscar_cadastro(email: str):
    """Retorna o cadastro do e-mail informado ou None se não existir."""
    resp = (
        _cliente()
        .table(TBL_CADASTRO)
        .select("*")
        .eq("email", normalizar_email(email))
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def criar_cadastro(nome: str, email: str, celular: str = "", idade: str = "", sexo: str = ""):
    """Cria o cadastro e o retorna. Se o e-mail já existir, retorna o existente."""
    dados = {
        "nome_completo": nome.strip(),
        "email": normalizar_email(email),
        "celular": celular.strip() or None,
        "idade": int(idade) if str(idade).strip() else None,
        "sexo": sexo or None,
    }
    try:
        resp = _cliente().table(TBL_CADASTRO).insert(dados).execute()
        return resp.data[0]
    except Exception:
        # Corrida: outro acesso cadastrou o mesmo e-mail no meio do caminho
        existente = buscar_cadastro(email)
        if existente:
            return existente
        raise


# ── Contexto do acesso (dispositivo, IP, navegador...) ──────────────────────
def analisar_user_agent(ua: str) -> dict:
    """Extrai dispositivo, sistema operacional e navegador do User-Agent."""
    ua = ua or ""
    if not ua:
        dispositivo = "desconhecido"
    elif re.search(r"bot|crawl|spider|slurp|headless", ua, re.I):
        dispositivo = "bot"
    elif re.search(r"iPad|Tablet", ua) or ("Android" in ua and "Mobile" not in ua):
        dispositivo = "tablet"
    elif re.search(r"Mobi|iPhone|iPod|Android", ua):
        dispositivo = "mobile"
    else:
        dispositivo = "desktop"

    sistemas = [
        (r"Windows", "Windows"),
        (r"Android", "Android"),
        (r"iPhone|iPad|iPod", "iOS"),
        (r"Mac OS X|Macintosh", "macOS"),
        (r"CrOS", "ChromeOS"),
        (r"Linux", "Linux"),
    ]
    sistema = next((nome for padrao, nome in sistemas if re.search(padrao, ua)), None)

    # A ordem importa: Edge, Opera e Samsung também se anunciam como Chrome
    navegadores = [
        (r"Edg(?:e|A|iOS)?/([\d.]+)", "Edge"),
        (r"OPR/([\d.]+)", "Opera"),
        (r"SamsungBrowser/([\d.]+)", "Samsung Internet"),
        (r"Firefox/([\d.]+)|FxiOS/([\d.]+)", "Firefox"),
        (r"Chrome/([\d.]+)|CriOS/([\d.]+)", "Chrome"),
        (r"Version/([\d.]+).*Safari", "Safari"),
    ]
    navegador = versao = None
    for padrao, nome in navegadores:
        m = re.search(padrao, ua)
        if m:
            navegador = nome
            versao = next((g for g in m.groups() if g), None)
            break

    return {
        "dispositivo": dispositivo,
        "sistema_operacional": sistema,
        "navegador": navegador,
        "versao_navegador": versao,
    }


def _ip_valido(valor):
    try:
        return str(ipaddress.ip_address((valor or "").strip()))
    except ValueError:
        return None


def contexto_acesso() -> dict:
    """Coleta o que o Streamlit expõe sobre o acesso atual."""
    ctx = st.context

    def _attr(nome):
        try:
            return getattr(ctx, nome, None)
        except Exception:
            return None

    headers = _attr("headers") or {}
    ua = headers.get("User-Agent", "") or ""

    # Atrás de proxy (Streamlit Cloud) o IP real vem em X-Forwarded-For
    encaminhado = (headers.get("X-Forwarded-For") or "").split(",")[0]
    ip = _ip_valido(encaminhado) or _ip_valido(headers.get("X-Real-Ip")) or _ip_valido(_attr("ip_address"))

    idioma = _attr("locale") or (headers.get("Accept-Language") or "").split(",")[0] or None

    return {
        "ip": ip,
        "user_agent": ua or None,
        **analisar_user_agent(ua),
        "idioma": idioma,
        "fuso_horario": _attr("timezone"),
        "url_acessada": _attr("url"),
        "origem_referrer": headers.get("Referer") or None,
    }


# ── Telemetria ──────────────────────────────────────────────────────────────
def registrar_evento(
    tipo_evento: str,
    cadastro_id=None,
    email: str = "",
    sucesso: bool = True,
    sessao_id=None,
    duracao_segundos=None,
    detalhes=None,
):
    """Grava um evento na telemetria. Nunca interrompe o app se falhar."""
    try:
        dados = {
            "tipo_evento": tipo_evento,
            "cadastro_id": cadastro_id,
            "email_informado": normalizar_email(email) or None,
            "sucesso": sucesso,
            "sessao_id": sessao_id,
            "duracao_segundos": duracao_segundos,
            "detalhes": detalhes or {},
            **contexto_acesso(),
        }
        _cliente().table(TBL_TELEMETRIA).insert(dados).execute()
        return True
    except Exception as e:
        log.warning("Falha ao gravar telemetria (%s): %s", tipo_evento, e)
        return False
