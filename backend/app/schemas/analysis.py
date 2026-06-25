from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., description="The text content to analyze for scam patterns")

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
