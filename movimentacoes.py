import sqlite3
import csv
import tkinter as tk
from tkinter import filedialog

# Conectar ao banco de dados
def conectar():
    return sqlite3.connect("financeiro.db")


# Registrar uma nova movimentação
def adicionar_movimentacao():
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

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes
        (descricao, valor, tipo, categoria, data)
        VALUES (?, ?, ?, ?, ?)
    """, (descricao, valor, tipo, categoria, data))

    conexao.commit()
    conexao.close()

    print("\nMovimentação adicionada com sucesso!")


# Listar todas as movimentações
def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, tipo, categoria, data
        FROM movimentacoes
    """)

    movimentacoes = cursor.fetchall()
    conexao.close()

    print("\n===== MOVIMENTAÇÕES =====")

    if not movimentacoes:
        print("Nenhuma movimentação cadastrada.")
        return

    for movimentacao in movimentacoes:
        print(
            f"ID: {movimentacao[0]} | "
            f"Descrição: {movimentacao[1]} | "
            f"Valor: R$ {movimentacao[2]:.2f} | "
            f"Tipo: {movimentacao[3]} | "
            f"Categoria: {movimentacao[4]} | "
            f"Data: {movimentacao[5]}"
        )


# Calcular saldo total
def calcular_saldo():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END),
            SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)
        FROM movimentacoes
    """)

    resultado = cursor.fetchone()
    conexao.close()

    receitas = resultado[0] or 0
    despesas = resultado[1] or 0
    saldo = receitas - despesas

    print("\n===== RESUMO FINANCEIRO =====")
    print(f"💰 Receitas: R$ {receitas:.2f}")
    print(f"💸 Despesas: R$ {despesas:.2f}")
    print("-----------------------------")
    print(f"💵 Saldo:    R$ {saldo:.2f}")


# Editar uma movimentação existente por ID
def editar_movimentacao():
    try:
        id_mov = int(input("\nDigite o ID da movimentação que deseja editar: "))
    except ValueError:
        print("ID inválido. Digite apenas números.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM movimentacoes WHERE id = ?", (id_mov,))
    movimentacao = cursor.fetchone()

    if not movimentacao:
        print(f"Nenhuma movimentação encontrada com o ID {id_mov}.")
        conexao.close()
        return

    print("\nDeixe em branco para manter o valor atual.")
    
    nova_desc = input(f"Nova descrição ({movimentacao[1]}): ").strip() or movimentacao[1]
    
    val_input = input(f"Novo valor ({movimentacao[2]}): ").strip()
    novo_valor = float(val_input) if val_input else movimentacao[2]

    novo_tipo = input(f"Novo tipo ({movimentacao[3]}): ").lower().strip() or movimentacao[3]
    nova_cat = input(f"Nova categoria ({movimentacao[4]}): ").strip() or movimentacao[4]
    nova_data = input(f"Nova data ({movimentacao[5]}): ").strip() or movimentacao[5]

    cursor.execute("""
        UPDATE movimentacoes
        SET descricao = ?, valor = ?, tipo = ?, categoria = ?, data = ?
        WHERE id = ?
    """, (nova_desc, novo_valor, novo_tipo, nova_cat, nova_data, id_mov))

    conexao.commit()
    conexao.close()

    print(f"\nMovimentação ID {id_mov} atualizada com sucesso!")


# Excluir uma movimentação por ID
def excluir_movimentacao():
    try:
        id_mov = int(input("\nDigite o ID da movimentação que deseja excluir: "))
    except ValueError:
        print("ID inválido. Digite apenas números.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM movimentacoes WHERE id = ?", (id_mov,))
    if not cursor.fetchone():
        print(f"Nenhuma movimentação encontrada com o ID {id_mov}.")
        conexao.close()
        return

    cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (id_mov,))
    conexao.commit()
    conexao.close()

    print(f"\nMovimentação ID {id_mov} excluída com sucesso!")


def exportar_csv():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, tipo, categoria, data
        FROM movimentacoes
    """)
    movimentacoes = cursor.fetchall()
    conexao.close()

    if not movimentacoes:
        print("\nNenhuma movimentação para exportar.")
        return

    # Oculta a janela principal do Tkinter
    root = tk.Tk()
    root.withdraw()

    # Abre a caixa de diálogo para escolher o local e o nome do arquivo
    caminho_arquivo = filedialog.asksaveasfilename(
        title="Salvar relatório como...",
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        initialfile="relatorio_financeiro.csv",
    )

    # Caso o usuário cancele a seleção
    if not caminho_arquivo:
        print("\nExportação cancelada pelo usuário.")
        return

    with open(
        caminho_arquivo, mode="w", newline="", encoding="utf-8-sig"
    ) as ficheiro:
        escritor = csv.writer(ficheiro, delimiter=";")
        escritor.writerow(
            ["ID", "Descrição", "Valor", "Tipo", "Categoria", "Data"]
        )
        escritor.writerows(movimentacoes)

    print(
        f"\nRelatório exportado com sucesso! Arquivo salvo em: {caminho_arquivo}"
    )

