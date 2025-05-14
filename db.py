import psycopg2
import chardet

def conectar():
    return psycopg2.connect(
        dbname="JobSync",      
        user="postgres",    
        password="postgres",
        host="localhost",        
        port="5432",
        options='-c client_encoding=UTF8'
    )

def limpar_unicode(texto):
    if isinstance(texto, bytes):
        detectado = chardet.detect(texto)
        try:
            return texto.decode(detectado['encoding'], errors='ignore')
        except Exception:
            return texto.decode('utf-8', errors='ignore')
    elif isinstance(texto, str):
        try:
            return texto.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        except Exception:
            return texto
    else:
        return str(texto)

def salvar_curriculo_no_banco(dados, curriculo_formatado):
    try:
        conn = conectar()
        cursor = conn.cursor()

        dados_limpos = {k: limpar_unicode(v) for k, v in dados.items()}
        curriculo_limpo = limpar_unicode(curriculo_formatado)

        cursor.execute("""
            INSERT INTO curriculos (
                nome, cargo, contato, experiencia, educacao, habilidades,
                projetos, idiomas, curriculo_gerado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            dados_limpos['nome'], dados_limpos['cargo'], dados_limpos['contato'],
            dados_limpos['experiencia'], dados_limpos['educacao'], dados_limpos['habilidades'],
            dados_limpos['projetos'], dados_limpos['idiomas'], curriculo_limpo
        ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Erro ao salvar no banco:", e)

def listar_curriculos():
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM curriculos ORDER BY id DESC")
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            return resultados  # Lista de tuplas: (id, nome)
        except Exception as e:
            print("Erro ao listar currículos:", e)
            return []
        
def obter_curriculo_por_id(curriculo_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT curriculo_gerado FROM curriculos WHERE id = %s", (curriculo_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado:
            return resultado[0]
        return None
    except Exception as e:
        print("Erro ao buscar currículo:", e)
        return None


