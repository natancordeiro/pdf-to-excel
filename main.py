import os

from utilitarios.extratores import ExtratorPDF
from utilitarios.logger_config import logger
from utilitarios.helper import *

def processa_pdfs(caminho_pasta:str, plano:str):
    """Processa os PDFs dentro da subpasta de um plano específico."""

    caminho_subpasta = os.path.join(caminho_pasta, plano)
    arquivos_pdf = [
        arquivo for arquivo in os.listdir(caminho_subpasta)
        if arquivo.endswith('.pdf')
    ]

    for arquivo in arquivos_pdf:
        caminho_pdf = os.path.join(caminho_subpasta, arquivo)
        extrator = ExtratorPDF(caminho_pdf, plano)
        dados = extrator.extrair_dados()
        logger.info(f"Dados extraídos: {dados}")

def main():
    # Caminho do arquivo de configuração
    caminho_config = 'config.ini'

    # Lendo configurações
    config = ler_configuracao(caminho_config)
    caminho_pasta = config['paths']['caminho_pasta']
    caminho_excel = config['paths']['caminho_excel']

    # Listando subpastas e processando PDFs
    subpastas = listar_subpastas(caminho_pasta)
    for subpasta in subpastas:
        processa_pdfs(caminho_pasta, subpasta)

    # Lendo o arquivo Excel
    dados_excel = ler_arquivo_excel(caminho_excel)
    if dados_excel is not None:
        salvar_dados(dados_excel)

if __name__ == '__main__':
    main()
