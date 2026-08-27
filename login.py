import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw

from database import NOME_BANCO, criar_tabela

# Configuração visual minimalista (tema claro estilo Microsoft)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def arredondar_imagem(caminho_imagem, tamanho=(48, 48), raio=12):
    """Carrega a imagem, redimensiona e aplica cantos arredondados."""
    img = Image.open(caminho_imagem).convert("RGBA").resize(tamanho, Image.Resampling.LANCZOS)
    
    mascara = Image.new("L", tamanho, 0)
    draw = ImageDraw.Draw(mascara)
    draw.rounded_rectangle((0, 0, tamanho[0], tamanho[1]), radius=raio, fill=255)
    
    img.putalpha(mascara)
    return img


class TelaLoginUnsainted(ctk.CTk):

    def __init__(self, callback_sucesso):
        super().__init__()

        criar_tabela()

        self.callback_sucesso = callback_sucesso

        self.title("Acesso ao Sistema")

        # Define o ícone da barra de título e da barra de tarefas
        try:
            self.iconbitmap("meu_icone.ico")
        except Exception:
            pass

        self.geometry("800x600")
        self.minsize(500, 500)
        self.configure(fg_color="#f2f2f2")

        self.etapa_atual = "usuario"
        self.usuario_atual = ""
        self.senha_banco_atual = ""
        self.mostrar_senha = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._criar_interface()

    def _criar_interface(self):
        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=430,
            fg_color="#ffffff",
            corner_radius=4,
            border_width=1,
            border_color="#e1e1e1",
        )
        self.card.grid(row=0, column=0)
        self.card.grid_propagate(False)
        self.card.grid_columnconfigure(0, weight=1)

        try:
            img_arredondada = arredondar_imagem("logo.png", tamanho=(48, 48), raio=12)
            imagem_logo = ctk.CTkImage(
                light_image=img_arredondada,
                dark_image=img_arredondada,
                size=(48, 48)
            )
            self.lbl_logo = ctk.CTkLabel(
                self.card,
                text="  Finance Control",
                image=imagem_logo,
                compound="left",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#1b1b1b",
            )
        except Exception:
            self.lbl_logo = ctk.CTkLabel(
                self.card,
                text="💼 Finance Control",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#1b1b1b",
            )

        self.lbl_logo.pack(anchor="w", padx=40, pady=(35, 10))

        self.lbl_titulo = ctk.CTkLabel(
            self.card,
            text="Entrar",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1b1b1b",
        )
        self.lbl_titulo.pack(anchor="w", padx=40, pady=(0, 20))

        self.frame_campo = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_campo.pack(fill="x", padx=40, pady=5)

        self.txt_entrada = ctk.CTkEntry(
            self.frame_campo,
            placeholder_text="Usuário",
            height=38,
            fg_color="#ffffff",
            border_color="#8a8a8a",
            border_width=1,
            corner_radius=2,
            text_color="#1b1b1b",
        )
        self.txt_entrada.pack(side="left", expand=True, fill="x")

        self.btn_olho = ctk.CTkButton(
            self.frame_campo,
            text="👁️",
            width=38,
            height=38,
            fg_color="#f0f0f0",
            hover_color="#e0e0e0",
            text_color="#000000",
            command=self._alternar_visibilidade_senha,
        )

        self.lbl_link = ctk.CTkLabel(
            self.card,
            text="Não tem uma conta? Crie uma!",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#0067b8",
            cursor="hand2",
        )
        self.lbl_link.pack(anchor="w", padx=40, pady=(15, 0))
        self.lbl_link.bind("<Button-1>", lambda e: self._abrir_modal_cadastro())

        self.frame_botoes = ctk.CTkFrame(self.card, fg_color="transparent")
        self.frame_botoes.pack(anchor="e", padx=40, pady=(35, 20))

        self.btn_voltar = ctk.CTkButton(
            self.frame_botoes,
            text="Voltar",
            width=90,
            height=32,
            fg_color="#cccccc",
            hover_color="#bbbbbb",
            text_color="#000000",
            corner_radius=2,
            command=self._voltar_etapa,
        )

        self.btn_avancar = ctk.CTkButton(
            self.frame_botoes,
            text="Avançar",
            width=90,
            height=32,
            fg_color="#0067b8",
            hover_color="#005da6",
            corner_radius=2,
            command=self._processar_avanco,
        )
        self.btn_avancar.pack(side="right")

        self.bind("<Return>", lambda event: self._processar_avanco())

    # ----------------------------------------------------------------------
    # BANCO DE DADOS
    # ----------------------------------------------------------------------
    def _buscar_usuario_banco(self, usuario):
        with sqlite3.connect(NOME_BANCO) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None

    def _cadastrar_usuario_banco(self, usuario, senha):
        with sqlite3.connect(NOME_BANCO) as conexao:
            cursor = conexao.cursor()
            
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
            if cursor.fetchone() is not None:
                return "DUPLICADO"

            try:
                cursor.execute(
                    "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                    (usuario, senha),
                )
                conexao.commit()
                return "SUCESSO"
            except sqlite3.Error:
                return "ERRO"

    # ----------------------------------------------------------------------
    # FLUXO DE LOGIN
    # ----------------------------------------------------------------------
    def _processar_avanco(self):
        if self.etapa_atual == "usuario":
            usuario_dig = self.txt_entrada.get().strip()
            if not usuario_dig:
                messagebox.showwarning("Atenção", "Informe o nome de usuário.")
                return

            senha_banco = self._buscar_usuario_banco(usuario_dig)

            if senha_banco:
                self.usuario_atual = usuario_dig
                self.senha_banco_atual = senha_banco
                self.etapa_atual = "senha"

                self.lbl_titulo.configure(text="Insira a senha")
                self.txt_entrada.delete(0, "end")
                self.txt_entrada.configure(placeholder_text="Senha", show="*")
                self.btn_olho.pack(side="right", padx=(5, 0))
                self.lbl_link.configure(text="Esqueceu a senha?")

                self.btn_voltar.pack(side="left", padx=(0, 10))
                self.btn_avancar.configure(text="Entrar")
            else:
                messagebox.showerror(
                    "Erro", "Não foi possível encontrar uma conta com esse usuário."
                )

        elif self.etapa_atual == "senha":
            senha_dig = self.txt_entrada.get().strip()
            if senha_dig == self.senha_banco_atual:
                self.destroy()
                self.callback_sucesso()
            else:
                messagebox.showerror("Erro", "Senha incorreta.")

    def _voltar_etapa(self):
        self.etapa_atual = "usuario"
        self.lbl_titulo.configure(text="Entrar")
        self.txt_entrada.delete(0, "end")
        self.txt_entrada.configure(placeholder_text="Usuário", show="")
        self.btn_olho.pack_forget()
        self.lbl_link.configure(text="Não tem uma conta? Crie uma!")

        self.btn_voltar.pack_forget()
        self.btn_avancar.configure(text="Avançar")

    def _alternar_visibilidade_senha(self):
        self.mostrar_senha = not self.mostrar_senha
        if self.mostrar_senha:
            self.txt_entrada.configure(show="")
            self.btn_olho.configure(text="🙈")
        else:
            self.txt_entrada.configure(show="*")
            self.btn_olho.configure(text="👁️")

    # ----------------------------------------------------------------------
    # JANELA DE CADASTRO
    # ----------------------------------------------------------------------
    def _abrir_modal_cadastro(self):
        janela_cad = ctk.CTkToplevel(self)
        janela_cad.title("Criar conta")
        janela_cad.geometry("380x350")
        janela_cad.configure(fg_color="#ffffff")
        janela_cad.grab_set()

        try:
            janela_cad.iconbitmap("meu_icone.ico")
        except Exception:
            pass

        lbl = ctk.CTkLabel(
            janela_cad,
            text="Criar nova conta",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1b1b1b"
        )
        lbl.pack(pady=(25, 15))

        txt_u = ctk.CTkEntry(
            janela_cad,
            placeholder_text="Escolha um Usuário",
            width=280,
            height=38,
            fg_color="#ffffff",
            border_color="#8a8a8a",
            border_width=1,
            corner_radius=2,
            text_color="#1b1b1b"
        )
        txt_u.pack(pady=8)

        frame_s = ctk.CTkFrame(janela_cad, fg_color="transparent")
        frame_s.pack(pady=8, padx=50, fill="x")

        txt_s = ctk.CTkEntry(
            frame_s,
            placeholder_text="Crie uma Senha",
            show="*",
            height=38,
            fg_color="#ffffff",
            border_color="#8a8a8a",
            border_width=1,
            corner_radius=2,
            text_color="#1b1b1b"
        )
        txt_s.pack(side="left", expand=True, fill="x")

        mostrar_senha_cad = [False]

        def alternar_senha_cad():
            mostrar_senha_cad[0] = not mostrar_senha_cad[0]
            if mostrar_senha_cad[0]:
                txt_s.configure(show="")
                btn_olho_cad.configure(text="🙈")
            else:
                txt_s.configure(show="*")
                btn_olho_cad.configure(text="👁️")

        btn_olho_cad = ctk.CTkButton(
            frame_s,
            text="👁️",
            width=38,
            height=38,
            fg_color="#f0f0f0",
            hover_color="#e0e0e0",
            text_color="#000000",
            corner_radius=2,
            command=alternar_senha_cad,
        )
        btn_olho_cad.pack(side="right", padx=(5, 0))

        def salvar():
            u, s = txt_u.get().strip(), txt_s.get().strip()
            if not u or not s:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return

            status = self._cadastrar_usuario_banco(u, s)
            
            if status == "DUPLICADO":
                messagebox.showerror(
                    "Usuário Indisponível",
                    f"O nome de usuário '{u}' já está em uso.\nPor favor, escolha um nome diferente!"
                )
                txt_u.delete(0, "end")
                txt_u.focus()
            elif status == "SUCESSO":
                messagebox.showinfo("Sucesso", "Conta criada com sucesso! Você já pode entrar.")
                janela_cad.destroy()
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao salvar o cadastro.")

        btn = ctk.CTkButton(
            janela_cad,
            text="Cadastrar Conta",
            fg_color="#0067b8",
            hover_color="#005da6",
            height=38,
            width=280,
            corner_radius=2,
            font=ctk.CTkFont(weight="bold"),
            command=salvar,
        )
        btn.pack(pady=20)


if __name__ == "__main__":
    from app import AppFinanceiro

    def iniciar_app_principal():
        app = AppFinanceiro()
        app.mainloop()

    tela = TelaLoginUnsainted(callback_sucesso=iniciar_app_principal)
    tela.mainloop()