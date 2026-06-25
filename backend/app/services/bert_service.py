import logging
import pickle
import torch
from typing import Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

class BertService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.tokenizer = None

    def load_model(self):
        try:
            with open(settings.BERT_MODEL_PATH, "rb") as f:
                self.model = torch.load(f, map_location=torch.device('cpu'))
            with open(settings.LABEL_ENCODER_PATH, "rb") as f:
                self.label_encoder = pickle.load(f)
            with open(settings.TOKENIZER_PATH, "rb") as f:
                self.tokenizer = pickle.load(f)
            logger.info("BERT models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load BERT models: {e}")

    async def classify(self, text: str) -> Tuple[str, float]:
        """
        Classifies the text to determine the scam type and confidence.
        Includes graceful degradation fallback.
        """
        try:
            # Placeholder for actual inference logic which might crash
            text_lower = text.lower()
            scam_type = "Legitimate"
            confidence = 0.95

            if "otp" in text_lower or "bank" in text_lower or "account" in text_lower:
                scam_type = "Bank Impersonation / OTP Fraud"
                confidence = 0.88
            elif "job" in text_lower or "salary" in text_lower:
                scam_type = "Job Scam"
                confidence = 0.75
            elif "winner" in text_lower or "lottery" in text_lower:
                scam_type = "Lottery Scam"
                confidence = 0.92
                
            return scam_type, confidence
        except Exception as e:
            logger.error(f"BERT Inference Failed. Engaging Fallback Rule Engine. Error: {e}")
            return "Unknown Threat (Fallback)", 0.0

bert_service = BertService()
