import google.generativeai as genai

API_KEY = "AIzaSyA90mSpQCPKjt8d-mRRD4gP94GsxVqf9KE"
GEMINI_MODEL = "gemini-1.5-flash-latest"
genai.configure(api_key=API_KEY)

def gerar_curriculo_gemini(dados):
    prompt = f"""
    Crie um currículo profissional, bem formatado, usando as informações abaixo:
    Nome: {dados['nome']}
    Cargo Desejado: {dados['cargo']}
    Contato: {dados['contato']}

    Experiência:
    {dados['experiencia']}

    Educação:
    {dados['educacao']}

    Habilidades:
    {dados['habilidades']}

    Projetos:
    {dados['projetos']}

    Idiomas:
    {dados['idiomas']}

    Retorne apenas o currículo em Português do Brasil, sem mensagens extras, sem dicas de como melhorar, de forma organizada e simples.
    """
    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Erro ao chamar Gemini:", e)
        return "Erro ao gerar currículo com a API do Gemini."
