from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NetworkNodeResponse(BaseModel):
    id: str
    type: str
    value: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class NetworkEdgeResponse(BaseModel):
    id: int
    source_id: str
    target_id: str
    relationship_type: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
