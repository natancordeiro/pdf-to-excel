import os

from utilitarios.extratores import ExtratorPDF
from utilitarios.logger_config import logger
from utilitarios.helper import *

def processa_pdfs(caminho_pasta:str, plano:str, formato_arquivo: str):
    """Processa os PDFs dentro da subpasta de um plano específico."""

    logger.info(f"Processando dados da plataforma {plano}")
    results = []

    caminho_subpasta = os.path.join(caminho_pasta, plano)
    arquivos_pdf = [
        arquivo for arquivo in os.listdir(caminho_subpasta)
        if arquivo.endswith('.pdf')
    ]
    logger.info(f"{len(arquivos_pdf)} Arquivos encontrados.")

    for i, arquivo in enumerate(arquivos_pdf):
        logger.info(f"Processando arquivo {arquivo} ({i+1}/{len(arquivos_pdf)})")
        caminho_pdf = os.path.join(caminho_subpasta, arquivo)
        extrator = ExtratorPDF(caminho_pdf, plano)
        dados = extrator.extrair_dados()
        logger.debug(f"Dados extraídos: {dados}")
        if dados:
            results.extend(dados)

    # Salvando dados em um arquivo
    if results:
        salvar_dados(results, plano, formato_arquivo)

def main():
    caminho_pasta = './pdfs'
    tipos_arquivos = ['csv', 'xlsx', 'json', 'xml', 'html']
    print(f"Qual o formato do arquivo que deseja extrair os dados? ")
    for i, tipo in enumerate(tipos_arquivos):
        print(f"{i+1} - {tipo}")
    
    escolha_formato = int(input("Escolha o número do formato: "))
    if escolha_formato - 1 < len(tipos_arquivos):
        formato_arquivo = tipos_arquivos[escolha_formato - 1]
        logger.info(f"Formato escolhido: {formato_arquivo}")
    else:
        logger.error("Formato inválido. Tente novamente.")
        return

    # Listando subpastas e processando PDFs
    subpastas = listar_subpastas(caminho_pasta)
    for subpasta in subpastas:
        processa_pdfs(caminho_pasta, subpasta, formato_arquivo)

    logger.info("Processamento finalizado.")

if __name__ == '__main__':
    main()
