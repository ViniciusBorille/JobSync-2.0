# ui.py (atualizado com LinkedIn)
from tkinter import Tk, Toplevel, Frame, Label, Entry, Text, Button, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
from gemini_api import gerar_curriculo_gemini
from arquivo import salvar_como_pdf, salvar_como_docx
from util import corrigir_caracteres
from linkedin_api import iniciar_login_linkedin, obter_dados_basicos

def iniciar_interface():
    root = Tk()
    root.title("Gerador de Currículos com Gemini")

    campos = {}

    def criar_campo(master, texto, altura=1):
        label = Label(master, text=texto, font=("Arial", 12, "bold"))
        label.pack(anchor="w")
        if altura == 1:
            entrada = Entry(master, font=("Arial", 12))
        else:
            entrada = Text(master, font=("Arial", 12), height=altura, width=50)
        entrada.pack(fill="x", pady=3)
        campos[texto] = entrada

    def obter_texto(campo):
        widget = campos[campo]
        return widget.get("1.0", "end").strip() if isinstance(widget, Text) else widget.get().strip()

    def mostrar_previa(texto):
        preview = Toplevel(root)
        preview.title("Prévia do Currículo")

        imagem_path = None
        img_label = Label(preview)
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

        Button(preview, text="Selecionar Imagem de Perfil", command=selecionar_imagem).pack(pady=5)

        texto_area = scrolledtext.ScrolledText(preview, font=("Arial", 12))
        texto_area.pack(expand=True, fill="both")
        texto_area.insert("1.0", texto)

        Button(preview, text="Salvar como PDF", command=lambda: salvar_como_pdf(texto_area.get("1.0", "end"), imagem_path)).pack(pady=5)
        Button(preview, text="Salvar como DOCX", command=lambda: salvar_como_docx(texto_area.get("1.0", "end"), imagem_path)).pack(pady=5)

    def gerar_e_mostrar():
        dados = {
            "nome": corrigir_caracteres(obter_texto("Nome")),
            "cargo": corrigir_caracteres(obter_texto("Cargo Desejado")),
            "contato": corrigir_caracteres(obter_texto("Contato")),
            "experiencia": obter_texto("Experiência"),
            "educacao": obter_texto("Educação"),
            "habilidades": obter_texto("Habilidades"),
            "projetos": obter_texto("Projetos"),
            "idiomas": obter_texto("Idiomas")
        }
        if not dados["nome"] or not dados["cargo"]:
            messagebox.showwarning("Campos obrigatórios", "Nome e Cargo são obrigatórios.")
            return
        texto = gerar_curriculo_gemini(dados)
        if "Erro" in texto:
            messagebox.showerror("Erro", texto)
            return
        mostrar_previa(texto)

    def preencher_exemplo():
        exemplos = {
            "Nome": "José da Silva",
            "Cargo Desejado": "Auxiliar Administrativo",
            "Contato": "(11) 98888-1234 | jose@email.com",
            "Experiência": "Empresa X | 2018 - 2023\nAtendimento ao Cliente",
            "Educação": "Ensino Médio Completo | Escola Estadual Y",
            "Habilidades": "Pacote Office\nComunicação\nOrganização",
            "Projetos": "Sistema de controle interno (descrição breve e concisa do projeto, se possível)",
            "Idiomas": "Português (Nativo)\nInglês (Básico)"
        }
        for campo, valor in exemplos.items():
            widget = campos[campo]
            if isinstance(widget, Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", valor)
            else:
                widget.delete(0, "end")
                widget.insert(0, valor)

    def importar_dados_do_linkedin():
        try:
            iniciar_login_linkedin()
            dados = obter_dados_basicos()
            if not dados:
                messagebox.showerror("Erro", "Não foi possível obter dados do LinkedIn.")
                return
            campos["Nome"].delete(0, "end")
            campos["Nome"].insert(0, dados["nome"])
            campos["Cargo Desejado"].delete(0, "end")
            campos["Cargo Desejado"].insert(0, dados["cargo"])
            campos["Contato"].delete("1.0", "end")
            campos["Contato"].insert("1.0", dados["contato"])
            messagebox.showinfo("Sucesso", "Dados importados do LinkedIn com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar do LinkedIn: {e}")

    frame = Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    for campo, altura in [
        ("Nome", 1), ("Cargo Desejado", 1), ("Contato", 3),
        ("Experiência", 5), ("Educação", 4), ("Habilidades", 4),
        ("Projetos", 4), ("Idiomas", 3)
    ]:
        criar_campo(frame, campo, altura)

    Button(root, text="Gerar Currículo", font=("Arial", 12), command=gerar_e_mostrar).pack(pady=5)
    Button(root, text="Preencher com Exemplo", font=("Arial", 12), command=preencher_exemplo).pack(pady=5)
    Button(root, text="Importar do LinkedIn", font=("Arial", 12), command=importar_dados_do_linkedin).pack(pady=5)

    root.mainloop()
