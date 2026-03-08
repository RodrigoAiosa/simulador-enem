import psycopg2
import socket
from datetime import datetime


HOST = "pg-2e2874e2-rodrigoaiosa-skydatasoluction.l.aivencloud.com"
PORT = "13191"
DATABASE = "BD_SKYDATA"
USER = "avnadmin"
PASSWORD = "AVNS_LlZukuJoh_0Kbj0dhvK"
SSL_MODE = "require"


# ─────────────────────────────────────────────
# Detectar dispositivo
# ─────────────────────────────────────────────
def detectar_dispositivo(user_agent:str=""):

    ua = user_agent.lower()

    if "android" in ua:
        return "Android"

    if "iphone" in ua or "ipad" in ua or "mac" in ua:
        return "Apple"

    if "windows" in ua or "linux" in ua:
        return "PC"

    return "Desconhecido"


# ─────────────────────────────────────────────
# Obter IP
# ─────────────────────────────────────────────
def obter_ip():

    try:

        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        s.connect(("8.8.8.8",80))

        ip=s.getsockname()[0]

        s.close()

        return ip

    except:

        return "0.0.0.0"


# ─────────────────────────────────────────────
# Registrar acesso
# ─────────────────────────────────────────────
def registrar_acesso(
    nome:str,
    celular:str,
    email:str,
    idade:str,
    sexo:str,
    user_agent:str="",
    duracao_segundos:int=0
):

    dispositivo = detectar_dispositivo(user_agent)

    ip = obter_ip()

    duracao = f"{duracao_segundos//60}min {duracao_segundos%60}s"


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

        cursor.execute(
            """
            INSERT INTO acesso_enem
            (data_hora,nome,celular,email,idade,sexo,dispositivo,ip,duracao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                datetime.now(),
                nome.strip(),
                celular,
                email,
                idade,
                sexo,
                dispositivo,
                ip,
                duracao
            )
        )

        conn.commit()

        print("Acesso registrado")

    except Exception as e:

        print("Erro:",e)

    finally:

        if 'conn' in locals():

            cursor.close()
            conn.close()
