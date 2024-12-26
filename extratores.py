import re
from PyPDF2 import PdfReader
from logger_config import logger

class ExtratorPDF:
    """Classe centralizada para extração de dados de PDFs."""

    def __init__(self, caminho_pdf, plano):
        self.caminho_pdf = caminho_pdf
        self.plano = plano
        self.dados = self.ler_pdf()

    def ler_pdf(self):
        """Faz a leitura inicial do PDF."""
        try:
            logger.info(f"Lendo PDF: {self.caminho_pdf}")
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
        else:
            logger.error(f"Plano de saúde desconhecido: {self.plano}")

    def _extrair_dados_odonto_empresas(self):
        """Extrai dados específicos do plano Odonto Empresas."""
        print("Extraindo dados do Odonto Empresas...")
        
        return {}

    def _extrair_dados_unimed(self):
        """Extrai dados específicos do plano Unimed."""

        logger.info("Extraindo dados do Unimed...")
        conteudo = self.dados.get("conteudo", "")
        results = []

        return results

    def _extrair_dados_rede_unna(self):
        """Extrai dados específicos do plano Rede Unna."""
        print("Extraindo dados do Rede Unna...")
        
        return {}
    
if __name__ == "__main__":
    # Exemplo de uso
    extrator = ExtratorPDF("./pdfs/unimed/unimed mes 09.pdf", "unimed")
    dados = extrator.extrair_dados()
    print(dados)