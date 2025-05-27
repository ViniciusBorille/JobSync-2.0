import re

def corrigir_caracteres(texto):
    texto = texto.replace("\u2013", "-").replace("\u2014", "--").replace("•", "-")
    return texto

def converter_markdown(linha):
    if re.match(r"^\*\*(.*?)\*\*$", linha):
        texto = re.sub(r"^\*\*(.*?)\*\*$", r"\1", linha)
        return texto, True
    else:
        texto = re.sub(r"\*\*(.*?)\*\*", r"\1", linha)
        texto = texto.replace("*", "")
        return texto, False