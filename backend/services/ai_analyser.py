import os
import google.generativeai as genai
import logging

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")

    async def analyze_company_data(self, company_data: dict) -> dict:
        prompt = f"""
        Analyze the following company data and return structured JSON:

        Company: {company_data.get('name')}
        Industry: {company_data.get('industry')}
        Website: {company_data.get('website')}
        Description: {company_data.get('description')}

        Provide:
        1. Business model
        2. Competitive advantages
        3. Market position
        4. Growth opportunities
        5. Potential challenges

        Format:
        {{
          "business_model": "...",
          "advantages": ["...", "..."],
          "market_position": "...",
          "opportunities": ["...", "..."],
          "challenges": ["...", "..."]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            return self._safe_json_parse(response.text)
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return {}

    async def generate_recommendations(self, context: dict) -> list:
        prompt = f"""
        Based on this context:

        Company: {context.get('target_company')}
        Industry: {context.get('industry')}
        Competitors: {', '.join([c['name'] for c in context.get('competitors', [])])}

        Suggest 5 strategic recommendations as a list.
        """
        try:
            response = self.model.generate_content(prompt)
            return self._extract_bullet_points(response.text)
        except Exception as e:
            logger.error(f"Gemini recommendation error: {e}")
            return []

    def _extract_bullet_points(self, text):
        lines = text.strip().splitlines()
        return [line.strip("•- ").strip() for line in lines if line.strip()]

    def _safe_json_parse(self, content: str) -> dict:
        import json
        try:
            return json.loads(content)
        except Exception:
            return {}