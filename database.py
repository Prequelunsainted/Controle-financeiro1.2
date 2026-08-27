import sqlite3

NOME_BANCO = "financeiro.db"


def conectar():
    """Retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(NOME_BANCO)


def criar_tabela():
    """Cria as tabelas necessárias no banco de dados se não existirem."""
    with conectar() as conexao:
        cursor = conexao.cursor()

        # Tabela de Movimentações
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

        # Tabela de Usuários
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
            """
        )

        # Insere um usuário padrão (admin / 1234) se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                ("admin", "1234"),
            )

        conexao.commit()