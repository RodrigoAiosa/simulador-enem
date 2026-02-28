import psycopg2
from datetime import datetime

# --- Configurações de Conexão ---
HOST = "pg-2e2874e2-rodrigoaiosa-skydatasoluction.l.aivencloud.com"
PORT = "13191"
DATABASE = "BD_SKYDATA"
USER = "avnadmin"
PASSWORD = "AVNS_LlZukuJoh_0Kbj0dhvK"
SSL_MODE = "require"

def registrar_acesso(nome: str):
    """Registra o acesso do usuário na tabela acesso_enem."""
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
            INSERT INTO acesso_enem (data_hora, nome)
            VALUES (%s, %s);
        """, (datetime.now(), nome.strip()))

        conn.commit()

    except Exception as e:
        print(f"Erro ao registrar acesso: {e}")

    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
