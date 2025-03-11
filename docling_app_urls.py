from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import json
import time
import requests
import os
from docling.document_converter import DocumentConverter

# Configurar opções do Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Modo sem interface gráfica
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Iniciar WebDriver
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

# Lista de URLs de leis
urls = [
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/legislacoes-federais",
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/decretos",
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/instrucoes-normativas",
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/cgsim/portarias-cgsim-1",
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/oficios-circulares",
    "https://www.gov.br/empresas-e-negocios/pt-br/drei/legislacao/consultas-publicas"
]

# Criar pasta para PDFs
os.makedirs("pdfs", exist_ok=True)

# Lista para armazenar os documentos extraídos
documentos = []

# Função para baixar e processar PDFs
def processar_pdf(url):
    try:
        nome_arquivo = f"pdfs/{url.split('/')[-1]}"  # Nome do arquivo
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(nome_arquivo, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"📥 PDF baixado: {nome_arquivo}")

            # Converter o PDF com Docling
            converter = DocumentConverter()
            result = converter.convert(nome_arquivo)
            markdown_text = result.document.export_to_markdown()
            return markdown_text
    except Exception as e:
        print(f"❌ Erro ao processar PDF {url}: {e}")
    return None

# Coletar todas as URLs de leis antes de navegar
urls_leis = []

for url in urls:
    driver.get(url)
    time.sleep(2)  # Pequena pausa para carregar a página

    try:
        tag_content = driver.find_element(By.ID, "content")  # Parte relevante da página
        links = tag_content.find_elements(By.XPATH, ".//a[@href]")
        for link in links:
            href = link.get_attribute("href")
            if href and re.search(r"\.(htm|pdf)", href):  # Verifica se tem .htm ou .pdf
                urls_leis.append(href)
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")

print(f"🔍 URLs coletadas: {len(urls_leis)}")

# Fechar o WebDriver principal
driver.quit()

# Processar cada URL de lei
for href in urls_leis:
    print(f"⚡ Processando: {href}")

    if ".pdf" in href:
        markdown_text = processar_pdf(href)
    else:
        try:
            # Criar um novo WebDriver para evitar StaleElementReferenceException
            driver = webdriver.Chrome(service=servico, options=chrome_options)
            driver.get(href)
            time.sleep(2)

            try:
                conteudo_lei = driver.find_element(By.TAG_NAME, "body").text  # Captura todo o texto da página
                markdown_text = f"# Lei extraída de {href}\n\n{conteudo_lei}"
            except:
                print(f"❌ Erro ao extrair texto de {href}")
                continue
            finally:
                driver.quit()  # Fechar WebDriver após processar cada página
        except Exception as e:
            print(f"❌ Erro ao acessar {href}: {e}")
            continue

    if markdown_text:
        documentos.append({"url": href, "conteudo": markdown_text})

# Salvar os documentos em JSON
with open("documentos_url_docling.json", "w", encoding="utf-8") as f:
    json.dump(documentos, f, ensure_ascii=False, indent=4)

print("✅ Processo concluído! Arquivo 'documentos_url_docling.json' gerado.")
