import os
import json
import fitz  # PyMuPDF

# Caminho onde os PDFs estão salvos
pasta_pdfs = "data"

# Lista para armazenar os documentos processados
documentos = []

# Processar cada PDF na pasta
for arquivo in os.listdir(pasta_pdfs):
    if arquivo.endswith(".pdf"):
        caminho_pdf = os.path.join(pasta_pdfs, arquivo)
        print(f"📄 Processando: {caminho_pdf}")

        try:
            # Abrir o PDF
            doc = fitz.open(caminho_pdf)
            texto = "\n".join([page.get_text("text") for page in doc])

            # Adicionar ao JSON
            documentos.append({"arquivo": arquivo, "conteudo": texto})
        except Exception as e:
            print(f"❌ Erro ao converter {arquivo}: {e}")

# Salvar os documentos em um JSON
with open("documentos_pdf_fitz.json", "w", encoding="utf-8") as f:
    json.dump(documentos, f, ensure_ascii=False, indent=4)

print("✅ Processo concluído! Arquivo 'documentos_pdf_fitz.json' gerado.")
