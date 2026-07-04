import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.network_repository import NetworkRepository
from cachetools import TTLCache
from app.services.auth_service import get_current_user
from app.database.models import User
from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

cache_store = TTLCache(maxsize=10, ttl=60)

@router.get("/network/graph")
@limiter.limit("60/minute")
async def get_network_graph(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns nodes and edges for the frontend network correlation graph.
    """
    cache_key = "network_graph"
    if cache_key in cache_store:
        return cache_store[cache_key]
        
    nodes = NetworkRepository.get_all_nodes(db)
    edges = NetworkRepository.get_all_edges(db)
    
    result = {
        "nodes": [
            {
                "id": n.id, 
                "type": n.node_type, 
                "value": n.node_value, 
                "risk_score": n.risk_score * 100 if n.risk_score <= 1.0 else n.risk_score,
                "first_seen": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else "Unknown",
                "last_seen": n.updated_at.strftime("%Y-%m-%d %H:%M:%S") if n.updated_at else "Unknown"
            } 
            for n in nodes
        ],
        "edges": [
            {
                "id": e.id, 
                "source": e.source_node_id, 
                "target": e.target_node_id, 
                "type": e.relationship_type or "linked_to", 
                "confidence": 1.0
            } 
            for e in edges
        ]
    }
    cache_store[cache_key] = result
    return result
