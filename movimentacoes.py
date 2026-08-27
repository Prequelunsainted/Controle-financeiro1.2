import csv
from database import conectar
from utils import formatar_moeda


class GerenciadorFinanceiro:

    def _conectar(self):
        return conectar()

    def adicionar_movimentacao(
        self, usuario_id, descricao, valor, tipo, categoria, data
    ):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO movimentacoes (usuario_id, descricao, valor, tipo, categoria, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (usuario_id, descricao, valor, tipo, categoria, data),
            )
            conexao.commit()

    def atualizar_movimentacao(
        self, id_mov, descricao, valor, tipo, categoria, data
    ):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE movimentacoes
                SET descricao = ?, valor = ?, tipo = ?, categoria = ?, data = ?
                WHERE id = ?
            """,
                (descricao, valor, tipo, categoria, data, id_mov),
            )
            conexao.commit()

    def excluir_movimentacao(self, id_mov):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (id_mov,))
            conexao.commit()

    def buscar_por_id(self, id_mov):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, descricao, valor, tipo, categoria, data FROM movimentacoes WHERE id = ?",
                (id_mov,),
            )
            return cursor.fetchone()

    def obter_totais(self, registros=None):
        """Calcula total de receitas, despesas e saldo a partir dos registros fornecidos ou do banco."""
        if registros is None:
            with self._conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN LOWER(tipo) = 'receita' THEN valor ELSE 0 END),
                        SUM(CASE WHEN LOWER(tipo) = 'despesa' THEN valor ELSE 0 END)
                    FROM movimentacoes
                """)
                res = cursor.fetchone()
                receitas = res[0] or 0.0
                despesas = res[1] or 0.0
        else:
            receitas = sum(
                r[2] for r in registros if str(r[3]).lower() == "receita"
            )
            despesas = sum(
                r[2] for r in registros if str(r[3]).lower() == "despesa"
            )

        saldo = receitas - despesas
        return receitas, despesas, saldo

    def exportar_csv(self, usuario_id=1, caminho_arquivo="relatorio_financeiro.csv"):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, descricao, valor, tipo, categoria, data FROM movimentacoes WHERE usuario_id = ? ORDER BY id DESC",
                (usuario_id,),
            )
            registros = cursor.fetchall()

        with open(
            caminho_arquivo, mode="w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                ["ID", "Descrição", "Valor", "Tipo", "Categoria", "Data"]
            )
            for reg in registros:
                id_mov, desc, val, tipo, cat, data = reg
                writer.writerow(
                    [id_mov, desc, formatar_moeda(val), tipo, cat, data]
                )