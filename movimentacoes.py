import sqlite3
import csv
import tkinter as tk
from tkinter import filedialog


class GerenciadorFinanceiro:
    """Classe responsável por gerenciar as operações de banco de dados e regras de negócio."""

    def __init__(self, db_name="financeiro.db"):
        self.db_name = db_name

    def _conectar(self):
        """Método privado para abrir conexão com o banco de dados."""
        return sqlite3.connect(self.db_name)

    def adicionar_movimentacao(self):
        descricao = input("Descrição: ").strip()
        while not descricao:
            print("A descrição não pode ficar vazia.")
            descricao = input("Descrição: ").strip()

        while True:
            try:
                valor = float(input("Valor: "))
                if valor <= 0:
                    print("O valor deve ser maior que zero.")
                    continue
                break
            except ValueError:
                print("Digite um valor válido. Exemplo: 150.50")

        while True:
            tipo = input("Tipo (receita/despesa): ").lower().strip()
            if tipo in ["receita", "despesa"]:
                break
            print("Digite apenas 'receita' ou 'despesa'.")

        categoria = input("Categoria: ").strip()
        while not categoria:
            print("A categoria não pode ficar vazia.")
            categoria = input("Categoria: ").strip()

        data = input("Data (DD/MM/AAAA): ").strip()
        while not data:
            print("A data não pode ficar vazia.")
            data = input("Data (DD/MM/AAAA): ").strip()

        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO movimentacoes (descricao, valor, tipo, categoria, data)
                VALUES (?, ?, ?, ?, ?)
            """, (descricao, valor, tipo, categoria, data))
            conexao.commit()

        print("\nMovimentação adicionada com sucesso!")

    def listar_movimentacoes(self):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, descricao, valor, tipo, categoria, data FROM movimentacoes")
            movimentacoes = cursor.fetchall()

        print("\n===== MOVIMENTAÇÕES =====")
        if not movimentacoes:
            print("Nenhuma movimentação cadastrada.")
            return

        for m in movimentacoes:
            print(f"ID: {m[0]} | Descrição: {m[1]} | Valor: R$ {m[2]:.2f} | Tipo: {m[3]} | Categoria: {m[4]} | Data: {m[5]}")

    def calcular_saldo(self):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END),
                    SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)
                FROM movimentacoes
            """)
            resultado = cursor.fetchone()

        receitas = resultado[0] or 0
        despesas = resultado[1] or 0
        saldo = receitas - despesas

        print("\n===== RESUMO FINANCEIRO =====")
        print(f"💰 Receitas: R$ {receitas:.2f}")
        print(f"💸 Despesas: R$ {despesas:.2f}")
        print("-----------------------------")
        print(f"💵 Saldo:    R$ {saldo:.2f}")

    def editar_movimentacao(self):
        try:
            id_mov = int(input("\nDigite o ID da movimentação que deseja editar: "))
        except ValueError:
            print("ID inválido. Digite apenas números.")
            return

        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM movimentacoes WHERE id = ?", (id_mov,))
            mov = cursor.fetchone()

            if not mov:
                print(f"Nenhuma movimentação encontrada com o ID {id_mov}.")
                return

            print("\nDeixe em branco para manter o valor atual.")
            nova_desc = input(f"Nova descrição ({mov[1]}): ").strip() or mov[1]
            val_input = input(f"Novo valor ({mov[2]}): ").strip()
            novo_valor = float(val_input) if val_input else mov[2]
            novo_tipo = input(f"Novo tipo ({mov[3]}): ").lower().strip() or mov[3]
            nova_cat = input(f"Nova categoria ({mov[4]}): ").strip() or mov[4]
            nova_data = input(f"Nova data ({mov[5]}): ").strip() or mov[5]

            cursor.execute("""
                UPDATE movimentacoes
                SET descricao = ?, valor = ?, tipo = ?, categoria = ?, data = ?
                WHERE id = ?
            """, (nova_desc, novo_valor, novo_tipo, nova_cat, nova_data, id_mov))
            conexao.commit()

        print(f"\nMovimentação ID {id_mov} atualizada com sucesso!")

    def excluir_movimentacao(self):
        try:
            id_mov = int(input("\nDigite o ID da movimentação que deseja excluir: "))
        except ValueError:
            print("ID inválido. Digite apenas números.")
            return

        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM movimentacoes WHERE id = ?", (id_mov,))
            if not cursor.fetchone():
                print(f"Nenhuma movimentação encontrada com o ID {id_mov}.")
                return

            cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (id_mov,))
            conexao.commit()

        print(f"\nMovimentação ID {id_mov} excluída com sucesso!")

    def exportar_csv(self):
        with self._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, descricao, valor, tipo, categoria, data FROM movimentacoes")
            movimentacoes = cursor.fetchall()

        if not movimentacoes:
            print("\nNenhuma movimentação para exportar.")
            return

        root = tk.Tk()
        root.withdraw()

        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar relatório como...",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            initialfile="relatorio_financeiro.csv"
        )

        if not caminho_arquivo:
            print("\nExportação cancelada pelo usuário.")
            return

        with open(caminho_arquivo, mode="w", newline="", encoding="utf-8-sig") as ficheiro:
            escritor = csv.writer(ficheiro, delimiter=";")
            escritor.writerow(["ID", "Descrição", "Valor", "Tipo", "Categoria", "Data"])
            escritor.writerows(movimentacoes)

        print(f"\nRelatório exportado com sucesso! Arquivo salvo em: {caminho_arquivo}")