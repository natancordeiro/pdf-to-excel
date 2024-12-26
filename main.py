import os
import configparser
import pandas as pd

from extratores import ExtratorPDF
from logger_config import logger


def ler_configuracao(caminho_config:str):
    """Lê o arquivo de configuração."""

    config = configparser.ConfigParser()
    config.read(caminho_config)
    return config

def listar_subpastas(caminho_pasta:str):
    """Lista as subpastas dentro do caminho especificado."""

    return [
        nome for nome in os.listdir(caminho_pasta) 
        if os.path.isdir(os.path.join(caminho_pasta, nome))
    ]

def processar_pdfs_por_plano(caminho_pasta:str, plano:str):
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

def ler_arquivo_excel(caminho_excel:str):
    """Lê o arquivo Excel especificado."""
    try:
        df = pd.read_excel(caminho_excel)
        return df
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo Excel: {e}")
        return None

def salvar_dados(df):
    """Salva os dados processados nos locais apropriados."""
    pass

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
        processar_pdfs_por_plano(caminho_pasta, subpasta)

    # Lendo o arquivo Excel
    dados_excel = ler_arquivo_excel(caminho_excel)
    if dados_excel is not None:
        salvar_dados(dados_excel)

if __name__ == '__main__':
    main()
