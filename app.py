from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image
from tkcalendar import Calendar

# Matplotlib para o Dashboard integrado ao Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from database import criar_tabela
from movimentacoes import GerenciadorFinanceiro
from utils import formatar_moeda, converter_para_float, validar_data

# Configurações globais de aparência do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CATEGORIAS_PADRAO = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Lazer",
    "Trabalho",
    "Tecnologia",
    "Cartão",
    "Investimentos",
    "Saúde",
    "Educação",
    "Outros",
]


class AppFinanceiro(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Inicializa infraestrutura
        criar_tabela()
        self.gerenciador = GerenciadorFinanceiro()

        # Controle de estado da visibilidade do formulário
        self.formulario_visivel = False

        # Configurações da Janela Principal
        self.title("Titanus Finance Control — Gestão Financeira Pessoal")
        self.geometry("1100x880")
        self.minsize(950, 700)

        # Configuração do Grid Principal
        # Configuração do Grid Principal (Abas na linha 5 expandem, rodapé fica visível na linha 6)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)

        # 1. Cabeçalho Minimalista
        self._criar_cabecalho()

        # 2. Cards Financeiros (KPIs)
        self._criar_cards_financeiros()

        # 3. Cards Financeiros (KPIs)
        self._criar_cards_financeiros()

        # 4. Filtros Avançados (Agrupado na linha 3)
        self._criar_area_filtros()

        # 5. Formulário de Cadastro (Agrupado na linha 4, logo abaixo do filtro)
        self._criar_formulario_cadastro()

        # 6. Dashboard / Gráficos + Tabela de Movimentações (Abas)
        self._criar_conteudo_principal()

        # Carregamento Inicial dos Dados
        self._atualizar_interface()

    # ----------------------------------------------------------------------
    # CONSTRUÇÃO DOS COMPONENTES VISUAIS
    # ----------------------------------------------------------------------

    def _criar_cabecalho(self):
        frame_cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        frame_cabecalho.grid(row=0, column=0, padx=25, pady=(15, 5), sticky="ew")

        # Lado Esquerdo: Imagem + Títulos
        frame_titulos = ctk.CTkFrame(frame_cabecalho, fg_color="transparent")
        frame_titulos.pack(side="left", anchor="w")

        # Caminho absoluto garantido para encontrar "titanus.png" na mesma pasta do script
        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho_logo = os.path.join(caminho_base, "titanus.png")

        if os.path.exists(caminho_logo):
            img_pil = Image.open(caminho_logo)
            self.img_behemoth = ctk.CTkImage(
                light_image=img_pil, dark_image=img_pil, size=(40, 40)
            )
            lbl_img = ctk.CTkLabel(frame_titulos, image=self.img_behemoth, text="")
            lbl_img.pack(side="left", padx=(0, 12))

        frame_textos = ctk.CTkFrame(frame_titulos, fg_color="transparent")
        frame_textos.pack(side="left", anchor="w")

        lbl_titulo = ctk.CTkLabel(
            frame_textos,
            text="Titanus Finance Control",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ctk.CTkLabel(
            frame_textos,
            text="Controle suas finanças de forma simples e intuitiva",
            font=ctk.CTkFont(size=13),
            text_color="#999999",
        )
        lbl_subtitulo.pack(anchor="w")

        # Lado Direito: Botão para abrir/fechar o formulário de adição
        self.btn_toggle_form = ctk.CTkButton(
            frame_cabecalho,
            text="➕ Nova Movimentação",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#1f538d",
            hover_color="#163c66",
            command=self._alternar_formulario,
        )
        self.btn_toggle_form.pack(side="right", anchor="e", pady=5)

        # Linha Divisória Discreta
        separador = ctk.CTkFrame(self, height=1, fg_color="#2b2b2b")
        separador.grid(row=1, column=0, padx=25, pady=(5, 10), sticky="ew")

    def _criar_cards_financeiros(self):
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.grid(row=2, column=0, padx=25, pady=5, sticky="ew")
        frame_cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # Card Receitas
        self.card_receita = ctk.CTkFrame(frame_cards, corner_radius=10, fg_color="#1e222d")
        self.card_receita.grid(row=0, column=0, padx=6, sticky="ew")
        ctk.CTkLabel(
            self.card_receita, text="Receitas", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa"
        ).pack(pady=(12, 2))
        self.lbl_val_receita = ctk.CTkLabel(
            self.card_receita, text="R$ 0,00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2FA572"
        )
        self.lbl_val_receita.pack(pady=(0, 12))

        # Card Despesas
        self.card_despesa = ctk.CTkFrame(frame_cards, corner_radius=10, fg_color="#1e222d")
        self.card_despesa.grid(row=0, column=1, padx=6, sticky="ew")
        ctk.CTkLabel(
            self.card_despesa, text="Despesas", font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaaaaa"
        ).pack(pady=(12, 2))
        self.lbl_val_despesa = ctk.CTkLabel(
            self.card_despesa, text="R$ 0,00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF5555"
        )
        self.lbl_val_despesa.pack(pady=(0, 12))

        # Card Saldo Final (Destaque Visual)
        self.card_saldo = ctk.CTkFrame(frame_cards, corner_radius=10, fg_color="#252a38", border_width=1, border_color="#3b4254")
        self.card_saldo.grid(row=0, column=2, padx=6, sticky="ew")
        ctk.CTkLabel(
            self.card_saldo, text="Saldo Atual", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cccccc"
        ).pack(pady=(12, 2))
        self.lbl_val_saldo = ctk.CTkLabel(
            self.card_saldo, text="R$ 0,00", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_val_saldo.pack(pady=(0, 12))

    def _criar_formulario_cadastro(self):
        self.frame_input = ctk.CTkFrame(self, corner_radius=10)

        self.txt_desc = ctk.CTkEntry(self.frame_input, placeholder_text="Descrição (ex: Supermercado)")
        self.txt_desc.pack(side="left", padx=8, pady=12, expand=True, fill="x")

        self.txt_valor = ctk.CTkEntry(self.frame_input, placeholder_text="Valor (ex: 150,50)", width=120)
        self.txt_valor.pack(side="left", padx=4, pady=12)

        self.combo_tipo = ctk.CTkComboBox(self.frame_input, values=["Receita", "Despesa"], width=110)
        self.combo_tipo.set("Despesa")
        self.combo_tipo.pack(side="left", padx=4, pady=12)

        self.combo_categoria = ctk.CTkComboBox(self.frame_input, values=CATEGORIAS_PADRAO, width=130)
        self.combo_categoria.set("Alimentação")
        self.combo_categoria.pack(side="left", padx=4, pady=12)

        self.txt_data_add = ctk.CTkEntry(self.frame_input, placeholder_text="DD/MM/AAAA", width=110)
        self.txt_data_add.pack(side="left", padx=(4, 0), pady=12)

        btn_cal = ctk.CTkButton(
            self.frame_input, text="📅", width=35, command=lambda: self._abrir_calendario(self.txt_data_add)
        )
        btn_cal.pack(side="left", padx=(2, 8), pady=12)

        btn_salvar = ctk.CTkButton(
            self.frame_input, text="💾 Salvar", width=90, font=ctk.CTkFont(weight="bold"), command=self._adicionar_registro
        )
        btn_salvar.pack(side="left", padx=(0, 4), pady=12)

        btn_fechar = ctk.CTkButton(
            self.frame_input,
            text="✖️",
            width=35,
            fg_color="#444444",
            hover_color="#333333",
            command=self._alternar_formulario,
        )
        btn_fechar.pack(side="left", padx=(0, 8), pady=12)

    def _alternar_formulario(self):
        if self.formulario_visivel:
            self.frame_input.grid_forget()
            self.btn_toggle_form.configure(text="➕ Nova Movimentação", fg_color="#1f538d")
            self.formulario_visivel = False
        else:
            self.frame_input.grid(row=3, column=0, padx=25, pady=10, sticky="ew")
            self.btn_toggle_form.configure(text="✖️ Fechar Formulário", fg_color="#444444")
            self.formulario_visivel = True
            self.txt_desc.focus()

    def _criar_area_filtros(self):
        frame_filtro = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtro.grid(row=3, column=0, padx=25, pady=(5, 5), sticky="ew")

        lbl_icon = ctk.CTkLabel(frame_filtro, text="🔍 Filtros:", font=ctk.CTkFont(weight="bold"))
        lbl_icon.pack(side="left", padx=(0, 8))

        self.combo_filtro_tipo = ctk.CTkComboBox(
            frame_filtro, values=["Todos", "Receita", "Despesa"], width=110, command=lambda c: self._atualizar_interface()
        )
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_tipo.pack(side="left", padx=4)

        cats_filtro = ["Todas"] + CATEGORIAS_PADRAO
        self.combo_filtro_cat = ctk.CTkComboBox(
            frame_filtro, values=cats_filtro, width=130, command=lambda c: self._atualizar_interface()
        )
        self.combo_filtro_cat.set("Todas")
        self.combo_filtro_cat.pack(side="left", padx=4)

        self.txt_filtro_data = ctk.CTkEntry(frame_filtro, placeholder_text="Data (DD/MM/AAAA)", width=140)
        self.txt_filtro_data.pack(side="left", padx=(8, 2))
        
        ctk.CTkButton(
            frame_filtro, text="📅", width=32, command=lambda: self._abrir_calendario(self.txt_filtro_data, auto_filtrar=True)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame_filtro, text="Filtrar", width=75, command=self._atualizar_interface
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            frame_filtro,
            text="🔄 Limpar",
            width=80,
            fg_color="#444444",
            hover_color="#333333",
            command=self._limpar_filtros,
        ).pack(side="left", padx=4)

    def _criar_conteudo_principal(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=5, column=0, padx=25, pady=5, sticky="nsew")

        self.tab_tabela = self.tabview.add("📊 Movimentações")
        self.tab_dash = self.tabview.add("📈 Dashboard & Gráficos")

        self._construir_tabela(self.tab_tabela)
        self._construir_dashboard(self.tab_dash)

    def _construir_tabela(self, aba):
        aba.grid_rowconfigure(0, weight=1)
        aba.grid_columnconfigure(0, weight=1)

        frame_tb = ctk.CTkFrame(aba, fg_color="transparent")
        frame_tb.grid(row=0, column=0, sticky="nsew")
        frame_tb.grid_rowconfigure(0, weight=1)
        frame_tb.grid_columnconfigure(0, weight=1)

        colunas = ("id", "descricao", "categoria", "tipo", "valor", "data")
        self.tabela = ttk.Treeview(frame_tb, columns=colunas, show="headings", style="Treeview")

        self.tabela.heading("id", text="ID")
        self.tabela.heading("descricao", text="Descrição")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("tipo", text="Tipo")
        self.tabela.heading("valor", text="Valor")
        self.tabela.heading("data", text="Data")

        self.tabela.column("id", width=0, stretch=False)
        self.tabela.column("descricao", width=260, anchor="w")
        self.tabela.column("categoria", width=140, anchor="center")
        self.tabela.column("tipo", width=110, anchor="center")
        self.tabela.column("valor", width=150, anchor="e")
        self.tabela.column("data", width=120, anchor="center")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1e222d",
            foreground="#ffffff",
            rowheight=32,
            fieldbackground="#1e222d",
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#151821",
            foreground="#aaaaaa",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", "#2b4c7e")])

        self.tabela.tag_configure("receita", foreground="#00FF0D")
        self.tabela.tag_configure("despesa", foreground="#FF0000")

        scrollbar = ctk.CTkScrollbar(frame_tb, orientation="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Barra de Ações na parte inferior da aba
        frame_acoes = ctk.CTkFrame(aba, fg_color="transparent")
        frame_acoes.grid(row=1, column=0, pady=(8, 0), sticky="ew")

        ctk.CTkButton(
            frame_acoes, text="✏️ Editar Selecionada", width=140, command=self._modal_editar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame_acoes,
            text="🗑️ Excluir Selecionada",
            width=140,
            fg_color="#8b2626",
            hover_color="#661c1c",
            command=self._confirmar_exclusao,
        ).pack(side="left")

        # Botão de Exportar CSV posicionado no canto direito da barra inferior
        ctk.CTkButton(
            frame_acoes,
            text="📁 Exportar Relatório CSV",
            fg_color="#1f538d",
            hover_color="#163c66",
            command=self._exportar_csv_acao,
        ).pack(side="right")

    def _construir_dashboard(self, aba):
        aba.grid_rowconfigure(0, weight=1)
        aba.grid_columnconfigure((0, 1), weight=1)

        self.frame_chart1 = ctk.CTkFrame(aba, fg_color="#1e222d", corner_radius=10)
        self.frame_chart1.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.frame_chart2 = ctk.CTkFrame(aba, fg_color="#1e222d", corner_radius=10)
        self.frame_chart2.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

    def _criar_rodape(self):
        frame_rodape = ctk.CTkFrame(self, fg_color="transparent")
        frame_rodape.grid(row=6, column=0, padx=25, pady=(5, 15), sticky="ew")

        btn_exportar = ctk.CTkButton(
            frame_rodape,
            text="📁 Exportar Relatório CSV",
            fg_color="#1f538d",
            hover_color="#163c66",
            command=self._exportar_csv_acao,
        )
        btn_exportar.pack(side="right")

    # ----------------------------------------------------------------------
    # LÓGICA E REGRAS DE NEGÓCIO
    # ----------------------------------------------------------------------

    def _abrir_calendario(self, entry_target, auto_filtrar=False):
        top = ctk.CTkToplevel(self)
        top.title("Selecione a Data")
        top.geometry("280x280")
        top.grab_set()
        top.resizable(False, False)

        hoje = datetime.now()
        cal = Calendar(
            top,
            selectmode="day",
            year=hoje.year,
            month=hoje.month,
            day=hoje.day,
            date_pattern="dd/mm/yyyy",
            background="#151821",
            foreground="white",
            headersbackground="#1e222d",
            selectbackground="#2b4c7e",
        )
        cal.pack(pady=10, padx=10, fill="both", expand=True)

        def selecionar():
            entry_target.delete(0, "end")
            entry_target.insert(0, cal.get_date())
            top.destroy()
            if auto_filtrar:
                self._atualizar_interface()

        ctk.CTkButton(top, text="Confirmar", command=selecionar).pack(pady=(0, 10))

    def _adicionar_registro(self):
        desc = self.txt_desc.get().strip()
        val_raw = self.txt_valor.get().strip()
        tipo = self.combo_tipo.get()
        cat = self.combo_categoria.get()
        data_raw = self.txt_data_add.get().strip()

        if not desc:
            messagebox.showwarning("Atenção", "Informe uma descrição para a movimentação.")
            return

        try:
            valor = converter_para_float(val_raw)
        except ValueError as e:
            messagebox.showerror("Valor Inválido", str(e))
            return

        try:
            data_validada = validar_data(data_raw)
        except ValueError as e:
            messagebox.showerror("Data Inválida", str(e))
            return

        self.gerenciador.adicionar_movimentacao(
            usuario_id=1,
            descricao=desc,
            valor=valor,
            tipo=tipo,
            categoria=cat,
            data=data_validada,
        )

        self.txt_desc.delete(0, "end")
        self.txt_valor.delete(0, "end")
        self.txt_data_add.delete(0, "end")

        self._alternar_formulario()

        messagebox.showinfo("Sucesso", "Movimentação registrada com sucesso.")
        self._atualizar_interface()

    def _obter_registros_filtrados(self):
        tipo_filtro = self.combo_filtro_tipo.get()
        cat_filtro = self.combo_filtro_cat.get()
        dt_filtro_str = self.txt_filtro_data.get().strip()

        dt_filtro = None
        if dt_filtro_str:
            try:
                dt_filtro = datetime.strptime(dt_filtro_str, "%d/%m/%Y")
            except ValueError:
                pass

        with self.gerenciador._conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, descricao, valor, tipo, categoria, data FROM movimentacoes ORDER BY id DESC"
            )
            todos = cursor.fetchall()

        filtrados = []
        for reg in todos:
            id_m, desc, val, tipo, cat, d_str = reg

            tipo_str = str(tipo) if tipo else ""
            cat_str = str(cat) if cat else "Geral"

            if tipo_filtro != "Todos" and tipo_str.lower() != tipo_filtro.lower():
                continue

            if cat_filtro != "Todas" and cat_str.lower() != cat_filtro.lower():
                continue

            if dt_filtro:
                try:
                    dt_reg = datetime.strptime(str(d_str), "%d/%m/%Y")
                    if dt_reg < dt_filtro:
                        continue
                except ValueError:
                    pass

            filtrados.append((id_m, desc, val, tipo_str, cat_str, d_str))

        return filtrados

    def _limpar_filtros(self):
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_cat.set("Todas")
        self.txt_filtro_data.delete(0, "end")
        self._atualizar_interface()

    def _atualizar_interface(self):
        registros = self._obter_registros_filtrados()

        rec, desp, saldo = self.gerenciador.obter_totais(registros)
        self.lbl_val_receita.configure(text=formatar_moeda(rec))
        self.lbl_val_despesa.configure(text=formatar_moeda(desp))

        cor_saldo = "#33FF00" if saldo >= 0 else "#FF5555"
        self.lbl_val_saldo.configure(text=formatar_moeda(saldo), text_color=cor_saldo)

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for reg in registros:
            id_m, desc, val, tipo, cat, d_str = reg
            sinal = "+ " if tipo.lower() == "receita" else "- "
            val_fmt = f"{sinal}{formatar_moeda(val)}"
            tag = "receita" if tipo.lower() == "receita" else "despesa"

            self.tabela.insert(
                "",
                "end",
                values=(id_m, desc, cat, tipo, val_fmt, d_str),
                tags=(tag,),
            )

        self._renderizar_graficos(registros)

    def _renderizar_graficos(self, registros):
        for w in self.frame_chart1.winfo_children():
            w.destroy()
        for w in self.frame_chart2.winfo_children():
            w.destroy()

        plt.style.use("dark_background")

        fig1, ax1 = plt.subplots(figsize=(4.5, 3), dpi=100)
        fig1.patch.set_facecolor("#1e222d")
        ax1.set_facecolor("#1e222d")

        rec = sum(r[2] for r in registros if str(r[3]).lower() == "receita")
        desp = sum(r[2] for r in registros if str(r[3]).lower() == "despesa")

        bars = ax1.bar(["Receitas", "Despesas"], [rec, desp], color=["#2FA572", "#FF5555"], width=0.5)
        ax1.set_title("Receitas vs Despesas", color="#ffffff", fontsize=11, fontweight="bold")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.tick_params(colors="#aaaaaa")

        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, yval, f"R${yval:.0f}", ha='center', va='bottom', color='#ffffff', fontsize=8)

        canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_chart1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        fig2, ax2 = plt.subplots(figsize=(4.5, 3), dpi=100)
        fig2.patch.set_facecolor("#1e222d")
        ax2.set_facecolor("#1e222d")

        cats_desp = {}
        for r in registros:
            if str(r[3]).lower() == "despesa":
                cat = r[4]
                cats_desp[cat] = cats_desp.get(cat, 0.0) + r[2]

        if cats_desp:
            labels = list(cats_desp.keys())
            valores = list(cats_desp.values())
            wedges, texts, autotexts = ax2.pie(
                valores, labels=labels, autopct="%1.0f%%", textprops=dict(color="#ffffff", fontsize=8), startangle=90
            )
            ax2.set_title("Gastos por Categoria", color="#ffffff", fontsize=11, fontweight="bold")
        else:
            ax2.text(0.5, 0.5, "Sem despesas no período", ha="center", va="center", color="#888888")
            ax2.axis("off")

        canvas2 = FigureCanvasTkAgg(fig2, master=self.frame_chart2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        plt.close(fig1)
        plt.close(fig2)

    def _modal_editar(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma linha da tabela para editar.")
            return

        item = self.tabela.item(sel[0])
        id_mov = item["values"][0]

        dados = self.gerenciador.buscar_por_id(id_mov)
        if not dados:
            return

        _, desc_orig, val_orig, tipo_orig, cat_orig, data_orig = dados

        modal = ctk.CTkToplevel(self)
        modal.title("Editar Movimentação")
        modal.geometry("400x420")
        modal.grab_set()
        modal.resizable(False, False)

        ctk.CTkLabel(modal, text="Editar Transação", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=12)

        txt_d = ctk.CTkEntry(modal, placeholder_text="Descrição", width=320)
        txt_d.insert(0, desc_orig)
        txt_d.pack(pady=6)

        txt_v = ctk.CTkEntry(modal, placeholder_text="Valor", width=320)
        txt_v.insert(0, str(val_orig))
        txt_v.pack(pady=6)

        cb_t = ctk.CTkComboBox(modal, values=["Receita", "Despesa"], width=320)
        cb_t.set(tipo_orig)
        cb_t.pack(pady=6)

        cb_c = ctk.CTkComboBox(modal, values=CATEGORIAS_PADRAO, width=320)
        cb_c.set(cat_orig)
        cb_c.pack(pady=6)

        txt_dt = ctk.CTkEntry(modal, placeholder_text="Data (DD/MM/AAAA)", width=320)
        txt_dt.insert(0, data_orig)
        txt_dt.pack(pady=6)

        def salvar():
            try:
                nv_desc = txt_d.get().strip()
                nv_val = converter_para_float(txt_v.get().strip())
                nv_dt = validar_data(txt_dt.get().strip())
                if not nv_desc:
                    raise ValueError("Descrição não pode ficar vazia.")

                self.gerenciador.atualizar_movimentacao(
                    id_mov, nv_desc, nv_val, cb_t.get(), cb_c.get(), nv_dt
                )
                modal.destroy()
                messagebox.showinfo("Sucesso", "Movimentação atualizada com sucesso.")
                self._atualizar_interface()
            except ValueError as ex:
                messagebox.showerror("Erro de Validação", str(ex))

        ctk.CTkButton(modal, text="💾 Salvar Alterações", command=salvar, width=320).pack(pady=15)

    def _confirmar_exclusao(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma movimentação para excluir.")
            return

        item = self.tabela.item(sel[0])
        id_mov = item["values"][0]
        desc = item["values"][1]

        resp = messagebox.askyesno(
            "Confirmar Exclusão", f"Tem certeza que deseja excluir a movimentação:\n'{desc}'?"
        )
        if resp:
            self.gerenciador.excluir_movimentacao(id_mov)
            messagebox.showinfo("Sucesso", "Movimentação excluída com sucesso.")
            self._atualizar_interface()

    def _exportar_csv_acao(self):
        caminho_arquivo = ctk.filedialog.asksaveasfilename(
            title="Salvar Relatório CSV",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            initialfile="relatorio_financeiro.csv"
        )
        if caminho_arquivo:
            try:
                # Caso a função exportar_csv aceite o caminho do arquivo:
                self.gerenciador.exportar_csv(caminho_arquivo)
                messagebox.showinfo("Exportação Concluída", f"Relatório exportado com sucesso em:\n{caminho_arquivo}")
            except TypeError:
                # Caso seu gerenciador salve com caminho fixo padrão:
                self.gerenciador.exportar_csv()
                messagebox.showinfo("Exportação Concluída", "Relatório CSV exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro ao Exportar", str(e))

if __name__ == "__main__":
    app = AppFinanceiro()
    app.mainloop()