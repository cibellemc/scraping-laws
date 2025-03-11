import os
import json
from docling.document_converter import DocumentConverter

# Caminho onde os PDFs estão salvos
pasta_pdfs = "data"

# Lista para armazenar os documentos processados
documentos = []

# Criar um conversor do Docling
converter = DocumentConverter()

# Processar cada PDF na pasta
for arquivo in os.listdir(pasta_pdfs):
    if arquivo.endswith(".pdf"):
        caminho_pdf = os.path.join(pasta_pdfs, arquivo)
        print(f"📄 Processando: {caminho_pdf}")

        try:
            # Converter com Docling
            result = converter.convert(caminho_pdf)
            markdown_text = result.document.export_to_markdown()
            documentos.append({"arquivo": arquivo, "conteudo": markdown_text})
        except Exception as e:
            print(f"❌ Erro ao converter {arquivo}: {e}")

# Salvar os documentos em um JSON
with open("documentos_pdf_docling.json", "w", encoding="utf-8") as f:
    json.dump(documentos, f, ensure_ascii=False, indent=4)

print("✅ Processo concluído! Arquivo 'documentos_pdf_docling.json' gerado.")
