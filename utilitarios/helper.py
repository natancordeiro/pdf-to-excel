import os 
import re
import pandas as pd
import configparser
from utilitarios.logger_config import logger

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

def find_previous_gto(procedure_start, gto_matches):
    for gto in reversed(gto_matches):
        if gto.end() < procedure_start:
            return gto.groups()
    return (None, None)

def obter_conteudo_parenteses(texto):
    ultimo_parentese = re.search(r'\(([^)]*)\)', texto)
    conteudo_parentese = ultimo_parentese.group(1) if ultimo_parentese else None
    return conteudo_parentese