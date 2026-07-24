import sqlite3
import os

# Detecta se existe a variável DATABASE_URL (só existe no Render, quando o
# PostgreSQL está conectado). Se não existir, é porque estamos rodando localmente.
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import psycopg2
    USANDO_POSTGRES = True
else:
    USANDO_POSTGRES = False

# SQLite usa "?" como marcador de parâmetro, PostgreSQL usa "%s".
# Centralizado aqui pra todos os módulos importarem o mesmo valor.
PLACEHOLDER = '%s' if USANDO_POSTGRES else '?'

CAMINHO_BANCO_LOCAL = os.path.join(os.path.dirname(__file__), 'banco.db')


def conectar():
    if USANDO_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(CAMINHO_BANCO_LOCAL)


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    # ID autoincremento tem sintaxe diferente entre SQLite e PostgreSQL
    id_autoincremento = "SERIAL PRIMARY KEY" if USANDO_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            senha TEXT NOT NULL
        )
    ''')

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS vencimentos (
            id {id_autoincremento},
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            lote TEXT,
            tipo TEXT,
            quantidade INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    ''')

    conexao.commit()
    conexao.close()
