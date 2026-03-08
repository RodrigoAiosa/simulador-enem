import sqlite3
from datetime import datetime


def registrar_acesso(
    nome,
    celular,
    email,
    idade,
    sexo,
    user_agent,
    duracao_segundos
):

    conn = sqlite3.connect("acessos.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acessos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        celular TEXT,
        email TEXT,
        idade TEXT,
        sexo TEXT,
        user_agent TEXT,
        duracao INTEGER,
        data TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO acessos (
        nome,
        celular,
        email,
        idade,
        sexo,
        user_agent,
        duracao,
        data
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        celular,
        email,
        idade,
        sexo,
        user_agent,
        duracao_segundos,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
