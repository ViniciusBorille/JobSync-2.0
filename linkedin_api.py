# linkedin_api.py (atualizado para usar .env)
import os
import requests
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
SCOPE = "r_liteprofile r_emailaddress"

access_token = None

def abrir_autenticacao():
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPE)}"
    )
    webbrowser.open(auth_url)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global access_token
        if self.path.startswith("/callback"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = params.get("code", [None])[0]
            if code:
                access_token = trocar_codigo_por_token(code)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Login com LinkedIn realizado com sucesso. Pode fechar esta janela.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Erro ao obter o codigo de autorizacao.")

def trocar_codigo_por_token(code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def obter_dados_basicos():
    global access_token
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}

    perfil = requests.get(
        "https://api.linkedin.com/v2/me?projection=(localizedFirstName,localizedLastName,headline)",
        headers=headers
    ).json()

    email = requests.get(
        "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
        headers=headers
    ).json()

    nome = f"{perfil.get('localizedFirstName', '')} {perfil.get('localizedLastName', '')}"
    cargo = perfil.get("headline", "")
    contato = email["elements"][0]["handle~"]["emailAddress"]

    return {
        "nome": nome,
        "cargo": cargo,
        "contato": contato
    }

def iniciar_login_linkedin():
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()
        abrir_autenticacao()
        input("Aperte ENTER apos o login no navegador...")
        httpd.shutdown()
