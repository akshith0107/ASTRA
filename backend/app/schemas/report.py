from pydantic import BaseModel
from typing import List
from datetime import datetime

class IndicatorBase(BaseModel):
    type: str
    value: str

class ReportResponse(BaseModel):
    id: int
    text_content: str
    risk_score: float
    risk_level: str
    scam_type: str
    confidence: float
    created_at: datetime
    indicators: List[dict] = []
    
    class Config:
        from_attributes = True
