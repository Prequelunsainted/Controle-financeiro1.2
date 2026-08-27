import sqlite3

# Altere de "finance.db" para "financeiro.db"
NOME_BANCO = "financeiro.db"


def conectar():
    """Retorna uma nova conexão com o banco de dados SQLite."""
    return sqlite3.connect(NOME_BANCO)


def criar_tabela():
    """Cria a tabela de movimentações se ela ainda não existir."""
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER DEFAULT 1,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT DEFAULT 'Geral',
                data TEXT NOT NULL
            )
        """
        )
        conexao.commit()