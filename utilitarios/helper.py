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

def salvar_dados(dados: list[dict], empresa: str, tipo_arquivo: str):
    """
    Salva os dados no formato desejado.

    Args:
        df (pd.DataFrame): DataFrame com os dados a serem salvos.
        empresa (str): Nome da empresa.
        tipo_arquivo (str): Formato de arquivo desejado (csv, xlsx).
    """

    df = pd.DataFrame(dados)

    if tipo_arquivo == "csv":
        df.to_csv(f"{empresa}_dados.csv", index=False)
    elif tipo_arquivo == "xlsx":
        df.to_excel(f"{empresa}_dados.xlsx", index=False)
    elif tipo_arquivo == "json":
        df.to_json(f"{empresa}_dados.json", orient="records")
    elif tipo_arquivo == "xml":
        df.to_xml(f"{empresa}_dados.xml", root_name="dados")
    elif tipo_arquivo == "html":
        df.to_html(f"{empresa}_dados.html", index=False)

    else:
        logger.error(f"Formato de arquivo inválido: {tipo_arquivo}")

def find_previous_gto(procedure_start, gto_matches):
    for gto in reversed(gto_matches):
        if gto.end() < procedure_start:
            return gto.groups()
    return (None, None)

def obter_conteudo_parenteses(texto):
    ultimo_parentese = re.search(r'\(([^)]*)\)', texto)
    conteudo_parentese = ultimo_parentese.group(1) if ultimo_parentese else None
    return conteudo_parentese