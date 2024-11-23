import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def obter_conteudo_do_site(url):
    """
    Faz uma requisição HTTP ao site e retorna o conteúdo HTML ou None em caso de erro.
    """
    try:
        resposta = requests.get(url)
        return resposta.text
    except Exception as e:
        print(f"Erro: {e}")
        return None

def verificar_js(js_conteudo, palavras_chave, url):
    """
    Verifica se o conteúdo de um arquivo JS contém palavras-chave sensíveis ou links suspeitos.
    """
    suspeitas = []

    for palavra in palavras_chave:
        if re.search(r'\b' + re.escape(palavra) + r'\b', js_conteudo.lower()):
            suspeitas.append(f"Palavra-chave '{palavra}' encontrada no conteúdo JavaScript.")

    return suspeitas

def verificar_site(url):
    """
    Verifica se o site apresenta sinais de ser fraudulento, incluindo a busca por informações sensíveis.
    """
    conteudo = obter_conteudo_do_site(url)
    if conteudo is None:
        return ["Não foi possível acessar o site."]

    suspeitas = []

    if not url.startswith('https://'):
        suspeitas.append("Atenção: O site não utiliza HTTPS")

    soup = BeautifulSoup(conteudo, 'html.parser')

    contato_tags = soup.find_all(string="contato")
    if not contato_tags:
        suspeitas.append("Atenção: O site não possui informações de contato visíveis.")

    palavras_chave = ['senha', 'cpf', 'email', 'cnpj', 'cartão de crédito', 'dados bancários', 'pix', 'rg']
    for palavra in palavras_chave:
        if palavra in conteudo.lower():
            suspeitas.append(f"Atenção: O site contém informações sensíveis como '{palavra}'")

    js_urls = [script['src'] for script in soup.find_all('script', src=True)]
    for js_url in js_urls:
        js_url_completa = urljoin(url, js_url)
        
        try:
            js_conteudo = requests.get(js_url_completa).text
            resultado_js = verificar_js(js_conteudo, palavras_chave, url)
            if resultado_js:
                for item in resultado_js:
                    suspeitas.append(f"Arquivo JS '{js_url_completa}' contém: {item}")
        except Exception as e:
            print(f"Erro: {js_url_completa}: {e}")

    if not suspeitas:
        suspeitas.append("O site parece ser seguro, mas uma análise mais aprofundada pode ser necessária.")

    return suspeitas


url = ""
resultado = verificar_site(url)

with open("scraping_site_malicioso.txt", 'w', encoding='utf-8') as arquivo_txt:
    verificacao = "Resultado da verificação:"
    arquivo_txt.write(verificacao)
    
    print(verificacao)
    for item in resultado:
        print(item)
        arquivo_txt.write(f"\n{item}")