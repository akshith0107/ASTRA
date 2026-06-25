from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    threat_level: str
    active_nodes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
