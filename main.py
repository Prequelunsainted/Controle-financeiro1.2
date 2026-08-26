from database import criar_tabela
from movimentacoes import (
    adicionar_movimentacao, 
    listar_movimentacoes, 
    calcular_saldo,
    excluir_movimentacao,
    editar_movimentacao,
    exportar_csv,
    buscar_por_categoria,
    buscar_por_data
)

criar_tabela()

while True:
    print("\n================================")
    print("       💰 FINANCE CONTROL")
    print("================================")
    print("1 - Adicionar movimentação")
    print("2 - Listar movimentações")
    print("3 - Ver saldo")
    print("4 - Editar movimentação")
    print("5 - Excluir movimentação")
    print("6 - Buscar por categoria")
    print("7 - Buscar por intervalo de datas")
    print("8 - Exportar relatório (CSV)")
    print("9 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        adicionar_movimentacao()
    elif opcao == "2":
        listar_movimentacoes()
    elif opcao == "3":
        calcular_saldo()
    elif opcao == "4":
        editar_movimentacao()
    elif opcao == "5":
        excluir_movimentacao()
    elif opcao == "6":
        buscar_por_categoria()
    elif opcao == "7":
        buscar_por_data()
    elif opcao == "8":
        exportar_csv()
    elif opcao == "9":
        print("\nPrograma encerrado. Até mais!")
        break
    else:
        print("\nOpção inválida. Tente novamente.")