import json
import logging
from decouple import config
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIHandler:
    """Service to handle OpenAI interactions"""

    def __init__(self):
        self.api_key = config('OPENAI_API_KEY', default='')
        self.model = config('OPENAI_MODEL', default='gpt-3.5-turbo')
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)

    def analyze_candidate(self, cv_text, criteria_list):
        """
        Analyzes a candidate's CV against a list of criteria.

        Args:
            cv_text (str): The text content of the CV.
            criteria_list (list): List of Criteria objects.

        Returns:
            dict: Analysis result containing scores and summary.
        """
        if not self.api_key:
            return {"error": "API Key missing"}

        prompt = self._build_prompt(cv_text, criteria_list)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR recruiter assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            # Fallback to Mock Data if API fails (e.g., quota exceeded)
            logger.warning("Falling back to MOCK AI mode due to API error.")
            return self._generate_mock_response(criteria_list)

    def _generate_mock_response(self, criteria_list):
        """Generates a dummy response for testing when API fails"""
        import random
        scores = {c.name: random.randint(2, 5) for c in criteria_list}
        return {
            "scores": scores,
            "summary": "[MOCK] Candidato apresenta boas qualificações gerais. Análise gerada automaticamente devido a erro na API (ex: cota excedida). Pontos fortes em diversas áreas."
        }

    def _build_prompt(self, cv_text, criteria_list):
        criteria_text = "\n".join([
            f"- {c.name} ({c.get_type_display()}): {c.description}" 
            for c in criteria_list
        ])

        return f"""
        Analyze the following Resume/CV text against the specified criteria.
        
        CRITERIA:
        {criteria_text}

        RESUME TEXT:
        {cv_text[:10000]}  # Limit text length to avoid token limits

        INSTRUCTIONS:
        1. Evaluate the candidate for EACH criterion on a scale of 0 to 5.
        2. Provide a brief summary of the candidate's key strengths and weaknesses relative to the position.
        3. Return the result in strict JSON format as follows:
        {{
            "scores": {{
                "Criteria Name 1": score,
                "Criteria Name 2": score
            }},
            "summary": "Brief professional summary..."
        }}
        """

    def calculate_total_score(self, analysis_data, criteria_list):
        """
        Calculates the weighted total score.
        """
        if "scores" not in analysis_data:
            return 0.0

        total_weight = 0
        weighted_sum = 0
        
        criteria_map = {c.name: c.weight for c in criteria_list}

        for criteria_name, score in analysis_data.get("scores", {}).items():
            # Match criteria name (fuzzy matching might be needed in production, but exact for now)
            # We assume the LLM returns the exact name we sent.
            weight = criteria_map.get(criteria_name, 1)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(weighted_sum / total_weight, 2)
