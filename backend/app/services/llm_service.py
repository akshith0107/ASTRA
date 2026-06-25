import logging
from typing import Dict, Any
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        # Groq uses the OpenAI python client with a custom base_url
        base_url = "https://api.groq.com/openai/v1"
        
        if AsyncOpenAI and api_key:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            self.model = "mixtral-8x7b-32768" # Default Groq model
            logger.info(f"LLMService initialized with model {self.model}")
        else:
            self.client = None
            logger.warning("GROQ_API_KEY not set or openai not installed. Using stubbed responses.")

    async def generate_threat_explanation(self, report_data: Dict[str, Any]) -> str:
        """
        Generates a natural language explanation of a detected threat.
        """
        if not self.client:
            return "Stubbed explanation: This report contains indicators of a known scam attempt."
            
        prompt = f"Explain the following threat report concisely to a security analyst: {report_data}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SentinelX, a senior cybersecurity threat analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Error generating threat explanation."

    async def generate_campaign_summary(self, campaign_name: str, reports: list) -> str:
        """
        Generates a summary of an ongoing threat campaign.
        """
        if not self.client:
            return f"Stubbed summary for campaign {campaign_name} based on {len(reports)} reports."
            
        prompt = f"Summarize the tactics, techniques, and procedures (TTPs) of this threat campaign: {campaign_name}. Data: {reports}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SentinelX, a senior cybersecurity threat analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Error generating campaign summary."

    async def generate_threat_summary(self, transcript: str, scam_type: str, indicators: list) -> str:
        """
        Generates a concise threat summary based on transcript and indicators.
        """
        if not self.client:
            return f"Stubbed threat summary for {scam_type}."
            
        prompt = f"Provide a 3-sentence threat summary for a {scam_type} scam containing these indicators: {indicators}. Transcript: {transcript[:200]}"
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cyber threat analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Error generating threat summary."

    async def generate_user_recommendations(self, scam_type: str) -> list[str]:
        """
        Generates actionable recommendations for the user based on the scam type.
        """
        if not self.client:
            return ["Do not share OTPs.", "Contact your bank immediately.", "Block the number."]
            
        prompt = f"Provide 3 concise, actionable security recommendations for a victim of a {scam_type} scam. Return them as a bulleted list."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cyber security advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            text = response.choices[0].message.content
            # Basic parsing of bullet points
            lines = [line.lstrip('-* ').strip() for line in text.split('\n') if line.strip() and (line.startswith('-') or line.startswith('*'))]
            return lines if lines else text.split('\n')
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ["Review account security.", "Report to authorities."]

llm_service = LLMService()
