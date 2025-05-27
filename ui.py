from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, Text, Button, messagebox,
    scrolledtext, filedialog, Canvas, VERTICAL, RIGHT, Y, LEFT, BOTH
)
from tkinter import ttk
from gemini_api import gerar_curriculo_gemini
from arquivo import salvar_como_pdf, salvar_como_docx
from util import corrigir_caracteres
from db import salvar_curriculo_no_banco, listar_curriculos, obter_curriculo_por_id

try:
    import ttkbootstrap as tb              
    StyleBase = tb.Style
    BTN_STYLE   = "success-outline"        
    THEME       = "flatly"                 
except ModuleNotFoundError:
    StyleBase = ttk.Style
    BTN_STYLE   = "RoundedButton.TButton"
    THEME       = "clam"                  

def configurar_estilo(root):
    style = StyleBase(theme=THEME)
    if BTN_STYLE == "RoundedButton.TButton":          
        style.configure(
            BTN_STYLE,
            background="#1572E8", foreground="white",
            borderwidth=0, padding=8, font=("Segoe UI", 11, "bold")
        )
        style.map(
            BTN_STYLE,
            background=[("active", "#0F59B5"), ("disabled", "#9bb8df")]
        )
    style.configure("FormLabel.TLabel", font=("Segoe UI", 10, "bold"))
    return style

def iniciar_interface():
    root = Tk()
    root.title("Gerador de Currículos com Gemini")
    root.geometry("500x650")
    style = configurar_estilo(root)

    campos = {}
    imagem_path = None

    container = Frame(root)
    container.pack(fill=BOTH, expand=True)

    canvas = Canvas(container, highlightthickness=0)
    vsb = ttk.Scrollbar(container, orient=VERTICAL, command=canvas.yview)
    form_frame = Frame(canvas, padx=16, pady=16)

    form_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=form_frame, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    vsb.pack(side=RIGHT, fill=Y)
    def criar_campo(texto, altura=1):
        lbl = ttk.Label(form_frame, text=texto, style="FormLabel.TLabel")
        lbl.pack(anchor="w", pady=(8 if campos else 0, 2))
        if altura == 1:
            entrada = ttk.Entry(form_frame, font=("Segoe UI", 11))
        else:
            entrada = Text(form_frame, font=("Segoe UI", 11),
                           height=altura, wrap="word", borderwidth=1,
                           relief="solid")
        entrada.pack(fill="x", expand=True)
        campos[texto] = entrada

    def obter_texto(campo):
        w = campos[campo]
        return w.get("1.0", "end").strip() if isinstance(w, Text) else w.get().strip()

    def selecionar_imagem():
        nonlocal imagem_path
        caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if caminho:
            imagem_path = caminho
            messagebox.showinfo("Imagem Selecionada", caminho)
    def mostrar_previa(texto):
        prev = Toplevel(root)
        prev.title("Prévia")
        scroller = scrolledtext.ScrolledText(prev, font=("Segoe UI", 10))
        scroller.insert("1.0", texto)
        scroller.pack(fill=BOTH, expand=True, padx=10, pady=10)

        pdf_btn  = ttk.Button(prev, text="Salvar PDF",
                              style=BTN_STYLE,
                              command=lambda: salvar_como_pdf(
                                  scroller.get("1.0", "end"), imagem_path))
        docx_btn = ttk.Button(prev, text="Salvar DOCX",
                              style=BTN_STYLE,
                              command=lambda: salvar_como_docx(
                                  scroller.get("1.0", "end"), imagem_path))
        pdf_btn.pack(side=LEFT, padx=10, pady=8)
        docx_btn.pack(side=LEFT, padx=0,  pady=8)
    def gerar_e_mostrar(event=None):
        dados = {
            "nome": corrigir_caracteres(obter_texto("Nome")),
            "cargo": corrigir_caracteres(obter_texto("Cargo Desejado")),
            "contato": corrigir_caracteres(obter_texto("Contato")),
            "experiencia": obter_texto("Experiência"),
            "educacao": obter_texto("Educação"),
            "habilidades": obter_texto("Habilidades"),
            "projetos": obter_texto("Projetos"),
            "idiomas": obter_texto("Idiomas"),
        }
        if not dados["nome"] or not dados["cargo"]:
            messagebox.showwarning("Campos obrigatórios",
                                   "Preencha Nome e Cargo.")
            return
        texto = gerar_curriculo_gemini(dados)
        if texto.startswith("Erro"):
            messagebox.showerror("Erro", texto)
            return
        salvar_curriculo_no_banco(dados, texto)
        mostrar_previa(texto)

    def carregar_curriculo(event=None):
        lista = listar_curriculos()
        if not lista:
            messagebox.showinfo("Sem registros",
                                "Nenhum currículo salvo.")
            return
        sel = Toplevel(root); sel.title("Currículos")
        ids = {f"{i} – {n}": i for i, n in lista}
        cb  = ttk.Combobox(sel, values=list(ids.keys()), width=40)
        cb.pack(padx=16, pady=16)

        def abrir():
            if cb.get():
                texto = obter_curriculo_por_id(ids[cb.get()])
                mostrar_previa(texto)
        ttk.Button(sel, text="Abrir", style=BTN_STYLE,
                   command=abrir).pack(pady=8)

    def preencher_exemplo(event=None):
        exemplo = {
            "Nome": "José da Silva",
            "Cargo Desejado": "Auxiliar Administrativo",
            "Contato": "Tel.: (11) 98888-1234\nE-mail: jose@email.com",
            "Experiência": "Empresa X (2018-2023) – Atendimento ao cliente",
            "Educação": "Ensino Médio – Escola Estadual Y",
            "Habilidades": "Pacote Office; Comunicação; Organização",
            "Projetos": "Sistema interno de controle",
            "Idiomas": "Português (nativo); Inglês (básico)",
        }
        for k, v in exemplo.items():
            w = campos[k]
            if isinstance(w, Text):
                w.delete("1.0", "end"); w.insert("1.0", v)
            else:
                w.delete(0, "end");    w.insert(0, v)

    ttk.Button(form_frame, text="Foto (opcional)", style=BTN_STYLE,
               command=selecionar_imagem).pack(anchor="e", pady=(0, 8))

    for c, h in [
        ("Nome", 1), ("Cargo Desejado", 1), ("Contato", 3),
        ("Experiência", 5), ("Educação", 4), ("Habilidades", 4),
        ("Projetos", 4), ("Idiomas", 3),
    ]:
        criar_campo(c, h)

    action_bar = Frame(root, pady=8)
    action_bar.pack(fill="x")

    ttk.Button(action_bar, text="Gerar Currículo",
               style=BTN_STYLE, command=gerar_e_mostrar).pack(side=LEFT, padx=8)
    ttk.Button(action_bar, text="Exemplo",
               style=BTN_STYLE, command=preencher_exemplo).pack(side=LEFT, padx=8)
    ttk.Button(action_bar, text="Currículos Salvos",
               style=BTN_STYLE, command=carregar_curriculo).pack(side=LEFT, padx=8)

    # atalhos
    root.bind("<Return>", gerar_e_mostrar)
    root.bind("<Control-e>", preencher_exemplo)
    root.bind("<Control-l>", carregar_curriculo)

    root.mainloop()
