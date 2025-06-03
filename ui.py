from tkinter import Tk, Toplevel, Frame, Label, Entry, Text, Button, messagebox, scrolledtext, filedialog, Listbox, SINGLE
from PIL import Image, ImageTk
from gemini_api import gerar_curriculo_gemini
from arquivo import salvar_como_pdf, salvar_como_docx
from util import corrigir_caracteres
from db import salvar_curriculo_no_banco, listar_curriculos, obter_curriculo_por_id

def iniciar_interface():
    root = Tk()
    root.title("Gerador de Currículos com Gemini")
    root.configure(bg="#e6f0fa")

    campos = {}

    def criar_campo(master, texto, altura=1):
        label = Label(master, text=texto, font=("Arial", 12, "bold"), bg="#e6f0fa", fg="#003366")
        label.pack(anchor="w", pady=(5, 0))
        entrada = Entry(master, font=("Arial", 12), relief="groove", bd=2) if altura == 1 else \
                  Text(master, font=("Arial", 12), height=altura, width=50, relief="groove", bd=2)
        entrada.pack(fill="x", pady=3, ipady=4)
        campos[texto] = entrada

    def obter_texto(campo):
        widget = campos[campo]
        return widget.get("1.0", "end").strip() if isinstance(widget, Text) else widget.get().strip()

    def mostrar_previa(texto):
        preview = Toplevel(root)
        preview.title("Prévia do Currículo")
        preview.configure(bg="#e6f0fa")
        imagem_path = None
        img_label = Label(preview, bg="#e6f0fa")
        img_label.pack(pady=5)

        def selecionar_imagem():
            nonlocal imagem_path
            caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
            if caminho:
                imagem_path = caminho
                try:
                    img = Image.open(caminho).resize((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    img_label.config(image=img_tk)
                    img_label.image = img_tk
                except Exception as e:
                    print("Erro ao carregar imagem:", e)

        Button(preview, text="🖼 Selecionar Imagem de Perfil", command=selecionar_imagem,
               bg="#336699", fg="white", font=("Arial", 11, "bold")).pack(pady=5)

        texto_area = scrolledtext.ScrolledText(preview, font=("Arial", 12))
        texto_area.pack(expand=True, fill="both")
        texto_area.insert("1.0", texto)

        Button(preview, text="📄 Salvar como PDF", command=lambda: salvar_como_pdf(texto_area.get("1.0", "end"), imagem_path),
               bg="#005580", fg="white", font=("Arial", 11, "bold")).pack(pady=5)

        Button(preview, text="📝 Salvar como DOCX", command=lambda: salvar_como_docx(texto_area.get("1.0", "end"), imagem_path),
               bg="#005580", fg="white", font=("Arial", 11, "bold")).pack(pady=5)

    def gerar_e_mostrar():
        dados = {chave: corrigir_caracteres(obter_texto(chave)) if chave in ["Nome", "Vaga Pretendida", "Contato"]
                 else obter_texto(chave) for chave in ["Nome", "Vaga Pretendida", "Contato", "Experiência", "Educação", "Habilidades", "Projetos", "Idiomas"]}
        if not dados["Nome"] or not dados["Vaga Pretendida"]:
            messagebox.showwarning("Campos obrigatórios", "Nome e Vaga Pretendida são obrigatórios.")
            return
        texto = gerar_curriculo_gemini(dados)
        if "Erro" in texto:
            messagebox.showerror("Erro", texto)
            return
        salvar_curriculo_no_banco(dados, texto)
        mostrar_previa(texto)

    def preencher_exemplo():
        exemplo = {
            "Nome": "José da Silva",
            "Vaga Pretendida": "Auxiliar Administrativo",
            "Contato": "(11) 98888-1234 | jose@email.com",
            "Experiência": "Empresa X | 2018 - 2023\nAtendimento ao Cliente",
            "Educação": "Ensino Médio Completo | Escola Estadual Y",
            "Habilidades": "Pacote Office\nComunicação\nOrganização",
            "Projetos": "Sistema de controle interno",
            "Idiomas": "Português (Nativo)\nInglês (Básico)"
        }
        for campo, valor in exemplo.items():
            widget = campos[campo]
            if isinstance(widget, Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", valor)
            else:
                widget.delete(0, "end")
                widget.insert(0, valor)

    def ver_curriculos_salvos():
        janela = Toplevel(root)
        janela.title("Currículos Salvos")
        janela.configure(bg="#e6f0fa")

        Label(janela, text="🔍 Filtrar por nome:", font=("Arial", 10, "bold"), bg="#e6f0fa", fg="#003366").pack()
        entrada_filtro = Entry(janela, font=("Arial", 12), relief="groove", bd=2)
        entrada_filtro.pack(pady=5)

        lista = Listbox(janela, width=50, height=15, selectmode=SINGLE, font=("Arial", 12))
        lista.pack(pady=10)

        todos = listar_curriculos()
        for id_, nome in todos:
            lista.insert("end", f"{id_} - {nome}")

        def filtrar():
            termo = entrada_filtro.get().lower()
            lista.delete(0, "end")
            for id_, nome in todos:
                if termo in nome.lower():
                    lista.insert("end", f"{id_} - {nome}")

        def visualizar():
            selecao = lista.curselection()
            if not selecao:
                messagebox.showwarning("Seleção necessária", "Selecione um currículo.")
                return
            linha = lista.get(selecao[0])
            id_curriculo = int(linha.split(" - ")[0])
            texto = obter_curriculo_por_id(id_curriculo)
            mostrar_previa(texto)

        Button(janela, text="🔍 Aplicar Filtro", command=filtrar,
               bg="#336699", fg="white", font=("Arial", 11, "bold")).pack(pady=2)

        Button(janela, text="👁 Visualizar", command=visualizar,
               bg="#003366", fg="white", font=("Arial", 11, "bold")).pack(pady=5)

    def aplicar_hover(botao, cor_hover, cor_original):
        botao.bind("<Enter>", lambda e: botao.config(bg=cor_hover))
        botao.bind("<Leave>", lambda e: botao.config(bg=cor_original))

    frame = Frame(root, padx=10, pady=10, bg="#e6f0fa")
    frame.pack(fill="both", expand=True)

    for campo, altura in [
        ("Nome", 1), ("Vaga Pretendida", 1), ("Contato", 3),
        ("Experiência", 5), ("Educação", 4), ("Habilidades", 4),
        ("Projetos", 4), ("Idiomas", 3)
    ]:
        criar_campo(frame, campo, altura)

    Label(frame, text="O currículo será personalizado de acordo com a vaga pretendida.",
          font=("Arial", 10), bg="#e6f0fa", fg="#003366").pack(anchor="w", pady=(0, 10))

    botoes_frame = Frame(root, bg="#e6f0fa")
    botoes_frame.pack(pady=12)

    btn_gerar = Button(botoes_frame, text="🚀 Gerar Currículo", font=("Arial", 12, "bold"),
                       bg="#003366", fg="white", relief="ridge", bd=3, width=20, command=gerar_e_mostrar)
    btn_gerar.pack(side="left", padx=10)
    aplicar_hover(btn_gerar, "#005599", "#003366")

    btn_exemplo = Button(botoes_frame, text="✨ Preencher com Exemplo", font=("Arial", 12, "bold"),
                         bg="#336699", fg="white", relief="ridge", bd=2, width=23, command=preencher_exemplo)
    btn_exemplo.pack(side="left", padx=10)
    aplicar_hover(btn_exemplo, "#4d88cc", "#336699")

    btn_ver = Button(botoes_frame, text="📂 Ver Currículos Salvos", font=("Arial", 12, "bold"),
                     bg="#005580", fg="white", relief="ridge", bd=2, width=23, command=ver_curriculos_salvos)
    btn_ver.pack(side="left", padx=10)
    aplicar_hover(btn_ver, "#0077aa", "#005580")

    root.mainloop()
