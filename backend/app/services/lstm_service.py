import os
import logging
from typing import Tuple
from app.models.lstm.predictor import BiLSTMPredictor

logger = logging.getLogger(__name__)

class LstmService:
    def __init__(self):
        self.is_loaded = False
        self.predictor = None

    def initialize(self):
        logger.info("Initializing BiLSTM Service...")
        
        # Path to where model and vocab are stored
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'lstm'))
        
        self.predictor = BiLSTMPredictor(model_dir)
        success = self.predictor.load()
        
        if success:
            self.is_loaded = True
            logger.info("BiLSTM Service fully loaded and ready for inference.")
        else:
            self.is_loaded = False
            logger.error("BiLSTM Service failed to initialize.")

    def map_risk_level(self, score: float) -> str:
        """Map prediction to: LOW, MEDIUM, HIGH, CRITICAL"""
        if score >= 0.85:
            return "CRITICAL"
        elif score >= 0.65:
            return "HIGH"
        elif score >= 0.40:
            return "MEDIUM"
        else:
            return "LOW"

    def predict_risk(self, transcript: str) -> Tuple[float, str, float]:
        """
        Executes sequential risk estimation on the transcript.
        Returns: (risk_score, risk_level, confidence)
        """
        if not self.is_loaded or not self.predictor:
            logger.warning("BiLSTM Service is offline. Returning safe defaults.")
            return 0.0, "UNKNOWN", 0.0
            
        if not transcript or not transcript.strip():
            return 0.0, "LOW", 1.0
            
        try:
            scam_prob, confidence = self.predictor.predict(transcript)
            risk_level = self.map_risk_level(scam_prob)
            
            logger.info(f"BiLSTM Inference complete: score={scam_prob:.3f} level={risk_level}")
            return float(scam_prob), risk_level, float(confidence)
            
        except Exception as e:
            logger.error(f"BiLSTM inference failed: {e}")
            return 0.0, "ERROR", 0.0

lstm_service = LstmService()
