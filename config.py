"""
Configurações do TalentScan
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações da aplicação"""
    
    # API OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    
    # Limites de processamento
    MAX_CV_LENGTH = int(os.getenv('MAX_CV_LENGTH', '3000'))  # Caracteres
    MAX_CANDIDATES = int(os.getenv('MAX_CANDIDATES', '100'))
    
    # Arquivos e diretórios
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', 'relatorios')
    LOG_FILE = os.getenv('LOG_FILE', 'talent_scan.log')
    
    # Formatação Excel
    EXCEL_HEADER_COLOR = os.getenv('EXCEL_HEADER_COLOR', '366092')
    EXCEL_GOOD_SCORE_COLOR = os.getenv('EXCEL_GOOD_SCORE_COLOR', 'C6EFCE')  # Verde
    EXCEL_MEDIUM_SCORE_COLOR = os.getenv('EXCEL_MEDIUM_SCORE_COLOR', 'FFEB9C')  # Amarelo
    EXCEL_BAD_SCORE_COLOR = os.getenv('EXCEL_BAD_SCORE_COLOR', 'FFC7CE')  # Vermelho
    
    # Configurações de análise
    MIN_SCORE_THRESHOLD = float(os.getenv('MIN_SCORE_THRESHOLD', '2.0'))
    REQUIRED_WEIGHT = int(os.getenv('REQUIRED_WEIGHT', '2'))
    DESIRED_WEIGHT = int(os.getenv('DESIRED_WEIGHT', '1'))
    
    @classmethod
    def validate(cls):
        """Valida as configurações"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY não configurada")
        elif not cls.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY parece inválida (deve começar com 'sk-')")
        
        if cls.OPENAI_MAX_TOKENS < 100:
            errors.append("OPENAI_MAX_TOKENS deve ser pelo menos 100")
        
        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            errors.append("OPENAI_TEMPERATURE deve estar entre 0 e 2")
        
        if cls.MAX_CV_LENGTH < 500:
            errors.append("MAX_CV_LENGTH deve ser pelo menos 500")
        
        if errors:
            raise ValueError("Erros de configuração: " + "; ".join(errors))
        
        return True
    
    @classmethod
    def get_score_color(cls, score: float) -> str:
        """Retorna a cor baseada na pontuação"""
        if score >= 4:
            return cls.EXCEL_GOOD_SCORE_COLOR
        elif score >= 3:
            return cls.EXCEL_MEDIUM_SCORE_COLOR
        else:
            return cls.EXCEL_BAD_SCORE_COLOR
