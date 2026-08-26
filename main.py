from database import criar_tabela
from movimentacoes import GerenciadorFinanceiro

# Garante a criação da tabela
criar_tabela()

# Instancia a classe
gerenciador = GerenciadorFinanceiro()

while True:
    print("\n================================")
    print("       💰 FINANCE CONTROL (POO)")
    print("================================")
    print("1 - Adicionar movimentação")
    print("2 - Listar movimentações")
    print("3 - Ver saldo")
    print("4 - Editar movimentação")
    print("5 - Excluir movimentação")
    print("6 - Exportar relatório (CSV)")
    print("7 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        gerenciador.adicionar_movimentacao()
    elif opcao == "2":
        gerenciador.listar_movimentacoes()
    elif opcao == "3":
        gerenciador.calcular_saldo()
    elif opcao == "4":
        gerenciador.editar_movimentacao()
    elif opcao == "5":
        gerenciador.excluir_movimentacao()
    elif opcao == "6":
        gerenciador.exportar_csv()
    elif opcao == "7":
        print("\nPrograma encerrado. Até mais!")
        break
    else:
        print("\nOpção inválida. Tente novamente.")