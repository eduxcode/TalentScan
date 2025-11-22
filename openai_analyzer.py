"""
Módulo para análise de currículos usando a API OpenAI
"""
import os
import json
import re
from typing import Dict, List, Any
from openai import OpenAI, RateLimitError, APIError
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    """Classe para análise de currículos usando OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        # Configurar cliente OpenAI com a sintaxe correta
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def parse_job_profile(self, profile_text: str) -> Dict[str, List[str]]:
        """
        Analisa o texto do perfil da vaga e extrai atributos
        
        Args:
            profile_text: Texto do perfil da vaga
            
        Returns:
            Dicionário com atributos requeridos e desejáveis
        """
        required_attributes = []
        desired_attributes = []
        
        current_section = None
        lines = profile_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar seção de atributos requeridos
            if 'requeridos' in line.lower() or 'obrigatórios' in line.lower():
                current_section = 'required'
                continue
            
            # Detectar seção de atributos desejáveis
            if 'desejáveis' in line.lower() or 'diferencial' in line.lower():
                current_section = 'desired'
                continue
            
            # Extrair atributos das linhas que começam com "-"
            if line.startswith('-'):
                attribute = line.strip('- ').strip()
                if attribute:  # Verificar se não está vazio
                    if current_section == 'required':
                        required_attributes.append(attribute)
                    elif current_section == 'desired':
                        desired_attributes.append(attribute)
        
        return {
            'requeridos': required_attributes,
            'desejaveis': desired_attributes
        }
    
    def analyze_cv(self, cv_text: str, job_profile: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analisa um currículo em relação ao perfil da vaga
        
        Args:
            cv_text: Texto do currículo
            job_profile: Perfil da vaga com atributos
            
        Returns:
            Dicionário com análise e pontuação
        """
        try:
            # Sanitize input to prevent prompt injection and limit length
            # Remove potential prompt injection markers
            safe_cv_text = cv_text.replace("```", "").replace("System:", "").replace("User:", "")
            
            # Limit length strictly
            max_length = 3000
            if len(safe_cv_text) > max_length:
                safe_cv_text = safe_cv_text[:max_length] + "... (truncated)"

            # Preparar prompt para análise
            required_attrs = '\n'.join([f"- {attr}" for attr in job_profile['requeridos']])
            desired_attrs = '\n'.join([f"- {attr}" for attr in job_profile['desejaveis']])
            
            prompt = f"""
Você é um especialista em RH analisando currículos. Analise o seguinte currículo em relação ao perfil da vaga e forneça uma pontuação de 1 a 5 para cada atributo (5 = muito aderente, 1 = não aderente).

PERFIL DA VAGA:

ATRIBUTOS REQUERIDOS:
{required_attrs}

ATRIBUTOS DESEJÁVEIS:
{desired_attrs}

CURRÍCULO PARA ANÁLISE:
{safe_cv_text}

INSTRUÇÕES:
1. Para cada atributo requerido e desejável, atribua uma nota de 1 a 5
2. Forneça um resumo das qualidades do candidato em relação ao perfil
3. Seja objetivo e baseie-se apenas nas informações presentes no currículo
4. Responda em formato JSON com a seguinte estrutura:
{{
    "pontuacoes": {{
        "atributo1": nota,
        "atributo2": nota,
        ...
    }},
    "resumo": "Resumo das qualidades do candidato em relação ao perfil da vaga"
}}

Responda APENAS com o JSON, sem texto adicional.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em RH que analisa currículos de forma objetiva e precisa."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Tentar extrair JSON da resposta
            try:
                # Remover possíveis markdown code blocks
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                analysis = json.loads(response_text)
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON da resposta: {e}")
                # Avoid logging full response text if it might contain PII reflected from input
                logger.debug(f"Resposta recebida (truncada): {response_text[:100]}...")
                
                # Fallback: tentar extrair informações manualmente
                return self._extract_analysis_fallback(response_text, job_profile)
                
        except RateLimitError as e:
            logger.error(f"Erro de Cota/Limite na API OpenAI: {e}")
            print("\n⚠️  ERRO CRÍTICO: Cota da API OpenAI excedida ou limite atingido.")
            print("   Por favor, verifique seu plano e detalhes de cobrança em: https://platform.openai.com/account/billing")
            print("   A análise continuará com valores padrão para não interromper o fluxo, mas os resultados não serão precisos.\n")
            return self._create_default_analysis(job_profile)
            
        except APIError as e:
            logger.error(f"Erro na API OpenAI: {e}")
            return self._create_default_analysis(job_profile)

        except Exception as e:
            logger.error(f"Erro na análise do currículo: {str(e)}")
            return self._create_default_analysis(job_profile)
    
    def _extract_analysis_fallback(self, response_text: str, job_profile: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Extrai análise de forma manual quando o JSON falha
        
        Args:
            response_text: Resposta da API
            job_profile: Perfil da vaga
            
        Returns:
            Análise extraída
        """
        pontuacoes = {}
        
        # Tentar extrair pontuações usando regex
        for attr in job_profile['requeridos'] + job_profile['desejaveis']:
            # Buscar padrões como "atributo: 4" ou "atributo - 4"
            pattern = rf'{re.escape(attr)}[:\-]\s*(\d)'
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                pontuacoes[attr] = int(match.group(1))
            else:
                pontuacoes[attr] = 1  # Nota padrão
        
        # Extrair resumo
        resumo = "Análise automática realizada. Verifique manualmente para detalhes."
        if "resumo" in response_text.lower():
            resumo_match = re.search(r'resumo[:\-]\s*(.+?)(?:\n|$)', response_text, re.IGNORECASE | re.DOTALL)
            if resumo_match:
                resumo = resumo_match.group(1).strip()
        
        return {
            "pontuacoes": pontuacoes,
            "resumo": resumo
        }
    
    def _create_default_analysis(self, job_profile: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Cria análise padrão quando há erro na API
        
        Args:
            job_profile: Perfil da vaga
            
        Returns:
            Análise padrão
        """
        pontuacoes = {}
        
        for attr in job_profile['requeridos'] + job_profile['desejaveis']:
            pontuacoes[attr] = 1  # Nota mínima
        
        return {
            "pontuacoes": pontuacoes,
            "resumo": "Erro na análise automática. Verificação manual necessária."
        }
    
    def calculate_total_score(self, analysis: Dict[str, Any], job_profile: Dict[str, List[str]]) -> float:
        """
        Calcula pontuação total ponderada
        
        Args:
            analysis: Análise do currículo
            job_profile: Perfil da vaga
            
        Returns:
            Pontuação total (0-5)
        """
        pontuacoes = analysis.get('pontuacoes', {})
        
        if not pontuacoes:
            return 0.0
        
        # Peso maior para atributos requeridos
        total_score = 0
        total_weight = 0
        
        # Atributos requeridos (peso 2)
        for attr in job_profile['requeridos']:
            if attr in pontuacoes:
                total_score += pontuacoes[attr] * 2
                total_weight += 2
        
        # Atributos desejáveis (peso 1)
        for attr in job_profile['desejaveis']:
            if attr in pontuacoes:
                total_score += pontuacoes[attr] * 1
                total_weight += 1
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight, 2)
