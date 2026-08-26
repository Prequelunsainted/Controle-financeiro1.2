import os
import customtkinter as ctk
from tkinter import ttk
from PIL import Image  # Certifique-se de ter instalado: pip install pillow
from database import criar_tabela
from movimentacoes import GerenciadorFinanceiro

# Configurações do tema CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppFinanceiro(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Inicializa banco de dados e gerenciador
        criar_tabela()
        self.gerenciador = GerenciadorFinanceiro()

        # Configurações da Janela Principal
        self.title("Finance Control - Gestão Financeira")
        self.geometry("850x800")
        self.minsize(750, 650)
        self.resizable(True, True)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Título do App
        self.lbl_titulo = ctk.CTkLabel(
            self, text="💰 Controle Financeiro", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_titulo.grid(row=0, column=0, pady=(15, 5), sticky="ew")

        # 2. Formulário de Cadastro
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.grid(row=1, column=0, pady=5, padx=20, sticky="ew")

        self.txt_descricao = ctk.CTkEntry(
            self.frame_inputs, placeholder_text="Descrição (ex: Mercado)"
        )
        self.txt_descricao.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.txt_valor = ctk.CTkEntry(
            self.frame_inputs, placeholder_text="Valor (ex: 150.00)", width=110
        )
        self.txt_valor.pack(side="left", padx=10, pady=10)

        self.combo_tipo = ctk.CTkComboBox(
            self.frame_inputs, values=["receita", "despesa"], width=110
        )
        self.combo_tipo.pack(side="left", padx=10, pady=10)

        self.btn_salvar = ctk.CTkButton(
            self.frame_inputs, text="➕ Adicionar", width=100, command=self._adicionar_registro
        )
        self.btn_salvar.pack(side="left", padx=10, pady=10)

        # 3. Filtro de Data
        self.frame_filtro = ctk.CTkFrame(self)
        self.frame_filtro.grid(row=2, column=0, pady=5, padx=20, sticky="ew")

        self.lbl_filtro = ctk.CTkLabel(
            self.frame_filtro, text="📅 Filtrar por Data:", font=ctk.CTkFont(weight="bold")
        )
        self.lbl_filtro.pack(side="left", padx=10, pady=10)

        dias = ["Todos"] + [f"{i:02d}" for i in range(1, 32)]
        meses = ["Todos"] + [f"{i:02d}" for i in range(1, 13)]
        anos = ["Todos", "2026", "2025", "2024"]

        self.combo_dia = ctk.CTkComboBox(
            self.frame_filtro,
            values=dias,
            width=80,
            command=lambda c: self._carregar_movimentacoes(),
        )
        self.combo_dia.set("Todos")
        self.combo_dia.pack(side="left", padx=5, pady=10)

        self.combo_mes = ctk.CTkComboBox(
            self.frame_filtro,
            values=meses,
            width=80,
            command=lambda c: self._carregar_movimentacoes(),
        )
        self.combo_mes.set("Todos")
        self.combo_mes.pack(side="left", padx=5, pady=10)

        self.combo_ano = ctk.CTkComboBox(
            self.frame_filtro,
            values=anos,
            width=90,
            command=lambda c: self._carregar_movimentacoes(),
        )
        self.combo_ano.set("Todos")
        self.combo_ano.pack(side="left", padx=5, pady=10)

        self.btn_limpar_filtro = ctk.CTkButton(
            self.frame_filtro,
            text="🔄 Limpar Filtros",
            width=100,
            fg_color="#555555",
            hover_color="#333333",
            command=self._limpar_filtros,
        )
        self.btn_limpar_filtro.pack(side="left", padx=15, pady=10)

        # 4. Painel de Resumo (Cards)
        self.frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resumo.grid(row=3, column=0, pady=5, padx=20, sticky="ew")
        self.frame_resumo.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_receita = ctk.CTkFrame(self.frame_resumo)
        self.card_receita.grid(row=0, column=0, padx=5, sticky="ew")
        self.lbl_tot_receita = ctk.CTkLabel(
            self.card_receita,
            text="Receitas\nR$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2FA572",
        )
        self.lbl_tot_receita.pack(pady=8)

        self.card_despesa = ctk.CTkFrame(self.frame_resumo)
        self.card_despesa.grid(row=0, column=1, padx=5, sticky="ew")
        self.lbl_tot_despesa = ctk.CTkLabel(
            self.card_despesa,
            text="Despesas\nR$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF5555",
        )
        self.lbl_tot_despesa.pack(pady=8)

        self.card_saldo = ctk.CTkFrame(self.frame_resumo)
        self.card_saldo.grid(row=0, column=2, padx=5, sticky="ew")
        self.lbl_saldo = ctk.CTkLabel(
            self.card_saldo,
            text="Saldo Final\nR$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_saldo.pack(pady=8)

        # Estilo das Tabelas
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            rowheight=28,
            fieldbackground="#2a2d2e",
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Treeview.Heading",
            background="#1f232a",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        self.style.map("Treeview", background=[("selected", "#1f538d")])

        # 5. Abas de Separação
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=4, column=0, pady=10, padx=20, sticky="nsew")

        self.tab_todas = self.tabview.add("Todas as Movimentações")
        self.tab_receitas = self.tabview.add("🟢 Apenas Receitas")
        self.tab_despesas = self.tabview.add("🔴 Apenas Despesas")

        self.tabela_todas = self._criar_tabela(self.tab_todas)
        self.tabela_receitas = self._criar_tabela(self.tab_receitas)
        self.tabela_despesas = self._criar_tabela(self.tab_despesas)

        # 6. Rodapé: Botão Exportar CSV + Imagem no Canto Inferior Esquerdo
        self.frame_rodape = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_rodape.grid(row=5, column=0, pady=(5, 15), padx=20, sticky="ew")

        # -------------------------------------------------------------
        # IMAGEM NO CANTO INFERIOR ESQUERDO
        # -------------------------------------------------------------
        caminho_imagem = "logo.png"

        if os.path.exists(caminho_imagem):
            img_pil = Image.open(caminho_imagem)
            # Imagem maior (60x60 px) alinhada à esquerda
            self.imagem_logo = ctk.CTkImage(
                light_image=img_pil, dark_image=img_pil, size=(60, 60)
            )
            self.lbl_logo = ctk.CTkLabel(self.frame_rodape, image=self.imagem_logo, text="")
            self.lbl_logo.pack(side="left", padx=(0, 10))

        # Botão centralizado no espaço restante
        self.btn_exportar = ctk.CTkButton(
            self.frame_rodape,
            text="📁 Exportar CSV Relatório",
            command=self.gerenciador.exportar_csv,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.btn_exportar.pack(side="left", expand=True)

        self._atualizar_saldo()
        self._carregar_movimentacoes()

    def _criar_tabela(self, aba):
        aba.grid_rowconfigure(0, weight=1)
        aba.grid_columnconfigure(0, weight=1)

        colunas = ("id", "descricao", "valor", "tipo", "categoria", "data")
        tabela = ttk.Treeview(aba, columns=colunas, show="headings", style="Treeview")

        tabela.heading("id", text="ID")
        tabela.heading("descricao", text="Descrição")
        tabela.heading("valor", text="Valor")
        tabela.heading("tipo", text="Tipo")
        tabela.heading("categoria", text="Categoria")
        tabela.heading("data", text="Data")

        tabela.column("id", width=60, anchor="center")
        tabela.column("descricao", width=220, anchor="center")
        tabela.column("valor", width=120, anchor="center")
        tabela.column("tipo", width=100, anchor="center")
        tabela.column("categoria", width=110, anchor="center")
        tabela.column("data", width=110, anchor="center")

        tabela.tag_configure("receita", foreground="#2FA572")
        tabela.tag_configure("despesa", foreground="#FF5555")

        scrollbar = ctk.CTkScrollbar(aba, orientation="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)

        tabela.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        return tabela

    def _adicionar_registro(self):
        desc = self.txt_descricao.get().strip()
        val_str = self.txt_valor.get().strip()
        tipo = self.combo_tipo.get()

        if not desc or not val_str:
            return

        try:
            valor = float(val_str)
        except ValueError:
            return

        with self.gerenciador._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO movimentacoes (descricao, valor, tipo, categoria, data)
                VALUES (?, ?, ?, ?, '26/08/2026')
            """,
                (desc, valor, tipo, "Geral"),
            )
            conexao.commit()

        self.txt_descricao.delete(0, "end")
        self.txt_valor.delete(0, "end")
        self._atualizar_saldo()
        self._carregar_movimentacoes()

    def _limpar_filtros(self):
        self.combo_dia.set("Todos")
        self.combo_mes.set("Todos")
        self.combo_ano.set("Todos")
        self._carregar_movimentacoes()

    def _carregar_movimentacoes(self):
        dia = self.combo_dia.get()
        mes = self.combo_mes.get()
        ano = self.combo_ano.get()

        padrao_dia = "__" if dia == "Todos" else dia
        padrao_mes = "__" if mes == "Todos" else mes
        padrao_ano = "____" if ano == "Todos" else ano

        padrao_busca = f"{padrao_dia}/{padrao_mes}/{padrao_ano}"

        with self.gerenciador._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                SELECT id, descricao, valor, tipo, categoria, data 
                FROM movimentacoes
                WHERE data LIKE ?
            """,
                (padrao_busca,),
            )
            registros = cursor.fetchall()

        for tab in (self.tabela_todas, self.tabela_receitas, self.tabela_despesas):
            for item in tab.get_children():
                tab.delete(item)

        if registros:
            self.style.configure("Treeview", gridcolor="#000000")

            for reg in registros:
                id_mov, desc, valor, tipo, cat, data = reg
                valor_fmt = f"R$ {valor:.2f}"
                tipo_lower = tipo.lower()
                tag_cor = "receita" if tipo_lower == "receita" else "despesa"
                item_dados = (
                    f"#{id_mov}",
                    desc,
                    valor_fmt,
                    tipo.capitalize(),
                    cat,
                    data,
                )

                self.tabela_todas.insert("", "end", values=item_dados, tags=(tag_cor,))

                if tipo_lower == "receita":
                    self.tabela_receitas.insert(
                        "", "end", values=item_dados, tags=("receita",)
                    )
                else:
                    self.tabela_despesas.insert(
                        "", "end", values=item_dados, tags=("despesa",)
                    )
        else:
            self.style.configure("Treeview", gridcolor="#2a2d2e")

    def _atualizar_saldo(self):
        with self.gerenciador._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END),
                    SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)
                FROM movimentacoes
            """)
            res = cursor.fetchone()

        rec = res[0] or 0
        desp = res[1] or 0
        saldo = rec - desp

        self.lbl_tot_receita.configure(text=f"Receitas\nR$ {rec:.2f}")
        self.lbl_tot_despesa.configure(text=f"Despesas\nR$ {desp:.2f}")

        cor_saldo = "#2FA572" if saldo >= 0 else "#FF5555"
        self.lbl_saldo.configure(
            text=f"Saldo Final\nR$ {saldo:.2f}", text_color=cor_saldo
        )


if __name__ == "__main__":
    app = AppFinanceiro()
    app.mainloop()