import sqlite3

DB_NAME = "agendamentos.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sala TEXT NOT NULL,
            data TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_agendamento(nome, sala, data, hora_inicio, hora_fim):
    if not check_conflito(sala, data, hora_inicio, hora_fim):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO agendamentos (nome, sala, data, hora_inicio, hora_fim) VALUES (?, ?, ?, ?, ?)", 
                  (nome, sala, data, hora_inicio, hora_fim))
        conn.commit()
        conn.close()
        return True
    return False

def get_agendamentos():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM agendamentos ORDER BY data, hora_inicio")
    data = c.fetchall()
    conn.close()
    return data

def delete_agendamento(id_agendamento):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM agendamentos WHERE id = ?", (id_agendamento,))
    conn.commit()
    conn.close()

def check_conflito(sala, data, inicio, fim):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT * FROM agendamentos
        WHERE sala = ?
        AND data = ?
        AND (
            (? < hora_fim AND ? > hora_inicio)
        )
    """, (sala, data, inicio, fim))
    conflito = c.fetchone()
    conn.close()
    return conflito is not None
