import psycopg2
import socket
from datetime import datetime

# --- Configurações de Conexão ---
HOST = "pg-2e2874e2-rodrigoaiosa-skydatasoluction.l.aivencloud.com"
PORT = "13191"
DATABASE = "BD_SKYDATA"
USER = "avnadmin"
PASSWORD = "AVNS_LlZukuJoh_0Kbj0dhvK"
SSL_MODE = "require"


def detectar_dispositivo(user_agent: str = "") -> str:
    """Detecta o tipo de dispositivo com base no User-Agent."""
    user_agent = user_agent.lower()
    if "android" in user_agent:
        return "Android"
    elif "iphone" in user_agent or "ipad" in user_agent or "mac" in user_agent:
        return "Apple"
    elif "windows" in user_agent or "linux" in user_agent or "x11" in user_agent:
        return "PC"
    else:
        return "Desconhecido"


def obter_ip() -> str:
    """Obtém o IP local da máquina."""
    try:
        # Cria conexão UDP fictícia para descobrir o IP de saída real
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"


def registrar_acesso(nome: str, user_agent: str = "", duracao_segundos: int = 0):
    """
    Registra o acesso do usuário na tabela acesso_enem.

    Parâmetros:
    - nome              : Nome do usuário
    - user_agent        : User-Agent do navegador/dispositivo (para detectar PC/Android/Apple)
    - duracao_segundos  : Tempo que o usuário ficou no simulador (em segundos)
    """
    dispositivo = detectar_dispositivo(user_agent)
    ip          = obter_ip()
    duracao     = f"{duracao_segundos // 60}min {duracao_segundos % 60}s"

    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            sslmode=SSL_MODE
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO acesso_enem (data_hora, nome, dispositivo, ip, duracao)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            datetime.now(),
            nome.strip(),
            dispositivo,
            ip,
            duracao
        ))
        conn.commit()
        print(f"✅ Acesso registrado | {nome} | {dispositivo} | {ip} | {duracao}")

    except Exception as e:
        print(f"❌ Erro ao registrar acesso: {e}")

    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
