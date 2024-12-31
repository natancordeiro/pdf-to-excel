import re
from PyPDF2 import PdfReader

from utilitarios.logger_config import logger
from utilitarios.helper import *

class ExtratorPDF:
    """Classe centralizada para extração de dados de PDFs."""

    def __init__(self, caminho_pdf, plano):
        self.caminho_pdf = caminho_pdf
        self.plano = plano
        self.dados = self.ler_pdf()

    def ler_pdf(self):
        """Faz a leitura inicial do PDF."""
        try:
            logger.debug(f"Lendo PDF: {self.caminho_pdf}")
            reader = PdfReader(self.caminho_pdf)
            texto = ""
            for pagina in reader.pages:
                texto += pagina.extract_text() or ""
            return {"conteudo": texto}
        except Exception as e:
            logger.error(f"Erro ao ler o PDF {self.caminho_pdf}: {e}")
            return {}

    def extrair_dados(self):
        """Chama o método de extração baseado no plano."""

        if self.plano == 'odonto_empresas':
            return self._extrair_dados_odonto_empresas()

        elif self.plano == 'unimed':
            return self._extrair_dados_unimed()

        elif self.plano == 'rede_unna':
            return self._extrair_dados_rede_unna()

        elif self.plano == 'amil':
            return self._extrair_dados_amil()

        elif self.plano == 'samp':
            return self._extrair_dados_samp()

        else:
            logger.error(f"Plano de saúde desconhecido: {self.plano}")

    def _extrair_dados_odonto_empresas(self):
        """Extrai dados específicos do plano Odonto Empresas."""

        logger.info("Extraindo dados do Odonto Empresas...")
        conteudo = self.dados.get("conteudo", "")
        results = []

        pattern = r"(\d{2}/\d{2}/\d{4})\s+(\d{6,8})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+(\d{6,8})"
        for procedure in re.finditer(pattern, conteudo):
            data, codigo_procedimento, valor_informado, valor_processado, valor_liberado, valor_glosa, numero_lote = procedure.groups()
            results.append({
                "Nome do Beneficiário": "",
                "Código Procedimento" : codigo_procedimento,
                "Valor Processado": valor_processado,
                "Valor Glosa": valor_glosa,
                "Data de Realização": data
            })

        logger.info(f"{len(results)} procedimentos extraidos.")
        return results

    def _extrair_dados_unimed(self):
        """Extrai dados específicos do plano Unimed."""

        logger.info("Extraindo dados do Unimed...")
        conteudo = self.dados.get("conteudo", "")
        results = []

        # Padrões das expressões regulares
        procedure_pattern = r"(\d{8}) ([A-ZÀ-Üà-ü :]+) (Pago|Não autorizado) (?:([A-Z]{1,5})\s)?(\d{1,2},\d{2}) (\d{1,2},\d{2}) (\d{1,2},\d{2})(?: (\d{2}/\d{2}/\d{4}))? ([A-ZÀ-Ü0-9]+)?"
        gto_pattern = r"GTO: CÓDIGO E NOME DO BENEFICIÁRIO: (\d{8}) \d{17} - ([A-Z ]+)"

        # Encontra os resultados dos GTOs e dos PROCEDIMENTOS   
        gto_matches = list(re.finditer(gto_pattern, conteudo))
        procedure_matches = list(re.finditer(procedure_pattern, conteudo))

        # Itera sobre os procedimentos e associa ao GTO correspondente
        for procedure in procedure_matches:
            gto_codigo, gto_nome = find_previous_gto(procedure.start(), gto_matches)
            if not gto_codigo:
                continue 

            # Extrair dados do procedimento
            procedure_data = procedure.groups()
            codigo_procedimento = procedure_data[0]
            nome_procedimento = procedure_data[1].strip()
            status = procedure_data[2]
            face = procedure_data[3] if procedure_data[3] else None
            valor_apresentado = procedure_data[4]
            valor_glosado = procedure_data[5]
            valor_pago = procedure_data[6]
            data_atendimento = procedure_data[7] if procedure_data[7] else None
            dt_area = procedure_data[8] if procedure_data[8] else None

            # Adicionar ao conjunto de dados
            results.append({
                "GTO": gto_codigo,
                "Nome do Beneficiário": gto_nome,
                "Código Procedimento": codigo_procedimento,
                "Nome Procedimento": nome_procedimento,
                "DT / Área": dt_area,
                "Face": face,
                "Status": status,
                "Valor Apresentado Conta": valor_apresentado,
                "Valor Glosado Conta": valor_glosado,
                "Valor Pago Conta": valor_pago,
                "Data de Atendimento": data_atendimento
            })

        logger.info(f"{len(results)} procedimentos extraidos.")
        return results

    def _extrair_dados_rede_unna(self):
        """Extrai dados específicos do plano Rede Unna."""

        logger.info("Extraindo dados do Rede Unna...")
        conteudo = self.dados.get("conteudo", "")
        results = []

        # Padrão para capturar o nome do beneficiário e os procedimentos
        beneficiario_pattern = r"(?P<nome_beneficiario>[A-Za-zÀ-ÿ\s]+?)12 - Nome Civil"
        procedure_pattern = r"""
            (?P<tabela>\d{2})\s+
            (?P<codigo_procedimento>\d{2}\.\d{3}\.\d{3})\s+
            (?P<nome_procedimento>(?:[A-Za-zÀ-ÿ0-9()./\s-]+?(?=\s(?:\d+|\b[A-Z]{2,}\b))))\s+
            (?P<dente_regiao>[A-Z]{2,}|\d+)\s+
            (?P<face>\w+)?\s*
            (?P<data>\d{2}/\d{2}/\d{4})\s+
            (?P<quantidade>\d{1,2})\s+
            (?P<valor_informado>\d+\.\d{2})\s+
            (?P<valor_processado>\d+\.\d{2})\s+
            (?P<valor_glosa>\d+\.\d{2})\s+
            (?P<valor_franquia>\d+\.\d{2})\s+
            (?P<valor_liberado>\d+\.\d{2})
        """

        # Compilar os padrões
        beneficiario_regex = re.compile(beneficiario_pattern)
        procedure_regex = re.compile(procedure_pattern, re.VERBOSE)

        # Encontrar todos os beneficiários no conteúdo
        beneficiario_matches = list(beneficiario_regex.finditer(conteudo))

        # Iterar sobre os beneficiários e procedimentos
        for i, beneficiario_match in enumerate(beneficiario_matches):
            nome_beneficiario = beneficiario_match.group("nome_beneficiario").strip()
            start = beneficiario_match.end()
            end = beneficiario_matches[i + 1].start() if i + 1 < len(beneficiario_matches) else len(conteudo)

            # Extrair procedimentos associados a esse beneficiário
            procedimentos_texto = conteudo[start:end]
            procedure_matches = procedure_regex.finditer(procedimentos_texto)

            for match in procedure_matches:
                results.append({
                    "Nome do Beneficiário": nome_beneficiario,
                    "Código Procedimento": match.group('codigo_procedimento'),
                    "Nome Procedimento": match.group('nome_procedimento'),
                    "Dente/Região": match.group('dente_regiao'),
                    "Face": match.group('face'),
                    "Valor Processado": match.group('valor_processado'),
                    "Valor Glosa": match.group('valor_glosa'),
                    "Data de Realização": match.group('data')
                })

        logger.info(f"{len(results)} procedimentos extraidos.")
        return results

    def _extrair_dados_samp(self):
        """Extrai dados específicos do plano SAMP."""

        logger.info("Extraindo dados do SAMP...")
        conteudo = self.dados.get("conteudo", "").replace('\n', ' ')
        procedure_pattern = r"(\d{2}/\d{2}/\d{4})DR\(A\)\.\s+([A-ZÀ-Ú]+(?:\s+[A-ZÀ-Ú]+)+)(\d{8,9})\s*-\s*([A-ZÀ-Ú]+(?:\s+[A-ZÀ-Ú]+)*)[^\w]*([A-ZÀ-Ú]+(?:\s+[A-ZÀ-Ú]+)*)\s*(\d{8})\s*-([A-ZÀ-Ú0-9À-Ú\s\-:,.()]+)\s*\[([^\]]+)\].*?R\$\s*([\d.,]+)"
        results = []

        for procedure in re.finditer(procedure_pattern, conteudo):
            data = procedure.group(1)
            # doutor = procedure.group(2)
            # id_paciente = procedure.group(3)
            first_name = procedure.group(4)
            last_name = procedure.group(5)
            codigo_procedimento = procedure.group(6)
            descricao = procedure.group(7)
            gto_codigo = procedure.group(8)
            valor = procedure.group(9)

            results.append({
                "GTO": gto_codigo.split('O')[-1].strip(),
                "Nome do Beneficiário": first_name + " " + last_name,
                "Código Procedimento": codigo_procedimento,
                "Nome Procedimento": descricao.split('(', -1)[0].strip(),
                "Face": obter_conteudo_parenteses(descricao),
                "Valor": valor,
                "Data de Atendimento": data
            })

        logger.info(f"{len(results)} procedimentos extraidos.")
        return results

    def _extrair_dados_amil(self):
        """Extrai dados específicos do plano Amil."""

        logger.info("Extraindo dados do Amil...")
        conteudo = self.dados.get("conteudo", "")
        results = []

        # Padrões regex
        beneficiary_pattern = r"Nome do Beneficiário\s*([A-ZÀ-Ü\s]+)"
        procedure_pattern = r"([A-ZÀ-Ü0-9()/ ]+(?: [A-ZÀ-Ü0-9()/ ]+)*?)\s+(\d{2}/\d{2}/\d{4})\s*([A-ZÀ-Ü()/\-]+)?\s+([\d.,]+)\s+([A-Z\d]+)\s+(\d{1,2})\s+(\d{8})\s+([\d.,]{1,5})\s*([\d.,]{1,4})\s+([\d.,]+)\s*([\d.,]+)"

        # Encontra os resultados dos beneficiários e procedimentos
        beneficiary_matches = list(re.finditer(beneficiary_pattern, conteudo))
        procedure_matches = list(re.finditer(procedure_pattern, conteudo))

        for procedure in procedure_matches:
            procedure_start = procedure.start()
            
            # Encontrar o Nome do Beneficiário anterior
            matching_beneficiary = None
            for beneficiary in beneficiary_matches:
                if beneficiary.start() < procedure_start:
                    matching_beneficiary = beneficiary.group(1).split('\n')[0].strip()
                else:
                    break
            
            if not matching_beneficiary:
                continue
            
            # Extrair os campos do procedimento
            descricao = procedure.group(1).strip()
            data_realizacao = procedure.group(2)
            face = procedure.group(3)
            dente_regiao = procedure.group(5)
            codigo_procedimento = procedure.group(7)
            valor_glosa_estorno = procedure.group(9)
            valor_processado = procedure.group(10)

            # valor_informado = procedure.group(4)
            # quantidade = procedure.group(6)
            # valor_liberado = procedure.group(8)
            # Separar Valor Franquia e Tabela
            # franquia_tabela = procedure.group(11).replace(",", ".")
            # valor_franquia = franquia_tabela[:-2]
            # tabela = franquia_tabela[-2:]
            
            results.append({
                "Nome do Beneficiário": matching_beneficiary,
                "Código Procedimento": codigo_procedimento,
                "Nome Procedimento": descricao,
                "Dente/Região": dente_regiao,
                "Face": face,
                "Valor Processado": valor_processado,
                "Valor Glosado/Estorno": valor_glosa_estorno,
                "Data de Realização": data_realizacao
            })

        logger.info(f"{len(results)} procedimentos extraidos.")
        return results
    
if __name__ == "__main__":

    # Exemplo de uso
    extrator = ExtratorPDF("./pdfs/unimed/unimed mes 09.pdf", "unimed")
    dados = extrator.extrair_dados()
    print(dados)
