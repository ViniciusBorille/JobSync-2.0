from tkinter import Tk, Toplevel, Frame, Label, Entry, Text, Button, messagebox, scrolledtext, ttk
from gemini_api import gerar_curriculo_gemini
from arquivo import salvar_como_pdf, salvar_como_docx
from util import corrigir_caracteres
from db import salvar_curriculo_no_banco, listar_curriculos, obter_curriculo_por_id
from tkinter import filedialog

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

    imagem_path = None  # variável global para armazenar caminho da imagem

    def selecionar_imagem():
        nonlocal imagem_path
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if caminho:
            imagem_path = caminho
            messagebox.showinfo("Imagem Selecionada", f"Imagem escolhida: {caminho}")

    def obter_texto(campo):
        widget = campos[campo]
        if isinstance(widget, Text):
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def mostrar_previa(texto):
        preview = Toplevel(root)
        preview.title("Prévia do Currículo")
        texto_area = scrolledtext.ScrolledText(preview, font=("Arial", 12))
        texto_area.pack(expand=True, fill="both")
        texto_area.insert("1.0", texto)

        Button(preview, text="Salvar como PDF", command=lambda: salvar_como_pdf(texto_area.get("1.0", "end"))).pack(pady=5)
        Button(preview, text="Salvar como DOCX", command=lambda: salvar_como_docx(texto_area.get("1.0", "end"))).pack(pady=5)

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
        salvar_curriculo_no_banco(dados, texto)
        mostrar_previa(texto)

    def carregar_curriculo():
        lista = listar_curriculos()
        if not lista:
            messagebox.showinfo("Nenhum currículo", "Nenhum currículo salvo encontrado.")
            return
        seletor = Toplevel(root)
        seletor.title("Selecionar Currículo")
        opcoes = [f"{id} - {nome}" for id, nome in lista]
        id_map = {f"{id} - {nome}": id for id, nome in lista}
        combo = ttk.Combobox(seletor, values=opcoes)
        combo.pack(padx=10, pady=10)
        def abrir():
            escolhido = combo.get()
            if escolhido:
                texto = obter_curriculo_por_id(id_map[escolhido])
                mostrar_previa(texto)
        Button(seletor, text="Abrir", command=abrir).pack(pady=5)

    def preencher_exemplo():
        exemplos = {
            "Nome": "José da Silva",
            "Cargo Desejado": "Auxiliar Administrativo",
            "Contato": "Telefone: (11) 98888-1234\nE-mail: jose@email.com",
            "Experiência": "Empresa X - 2018 a 2023\nFunção: Atendimento ao Cliente",
            "Educação": "Ensino Médio Completo - Escola Estadual Y",
            "Habilidades": "Pacote Office, Comunicação, Organização",
            "Projetos": "Sistema de controle interno",
            "Idiomas": "Português (Nativo), Inglês (Básico)"
        }
        for campo, valor in exemplos.items():
            widget = campos[campo]
            if isinstance(widget, Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", valor)
            else:
                widget.delete(0, "end")
                widget.insert(0, valor)

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
    Button(root, text="Ver Currículos Salvos", font=("Arial", 12), command=carregar_curriculo).pack(pady=5)

    root.mainloop()
