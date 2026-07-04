from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from pydantic import model_validator

class AnalyzeTextRequest(BaseModel):
    text: Optional[str] = Field(None, description="The text content to analyze for scam patterns")
    text_content: Optional[str] = Field(None, description="The text content to analyze (legacy/frontend payload)")

    @model_validator(mode='after')
    def normalize_text(self) -> 'AnalyzeTextRequest':
        if not self.text and not self.text_content:
            raise ValueError('Either text or text_content must be provided')
        if not self.text and self.text_content:
            self.text = self.text_content
        if not self.text_content and self.text:
            self.text_content = self.text
        return self

class Indicator(BaseModel):
    type: str
    description: str
    confidence: float

class SimilarScam(BaseModel):
    campaign_name: str
    similarity_score: float
    scam_type: str

class AnalyzeResponse(BaseModel):
    risk_score: float = Field(..., description="Risk score from 0.0 to 100.0")
    risk_level: str = Field(..., description="SAFE, SUSPICIOUS, HIGH_RISK, or CRITICAL")
    scam_type: str = Field(..., description="The classified type of the scam")
    confidence: float = Field(..., description="Model confidence in the classification")
    indicators: List[Indicator] = Field(default_factory=list, description="List of specific heuristic indicators found")
    transcript: Optional[str] = Field(None, description="Transcribed text if audio was provided")
    language: Optional[str] = Field(None, description="Detected language of audio")
    similar_scams: List[SimilarScam] = Field(default_factory=list, description="Similar scams found in ChromaDB")
    lstm_risk_score: Optional[float] = Field(None, description="Sequential risk score from BiLSTM")
    lstm_risk_level: Optional[str] = Field(None, description="Sequential risk level from BiLSTM")
    lstm_confidence: Optional[float] = Field(None, description="Sequential confidence from BiLSTM")
