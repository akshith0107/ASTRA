from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.auth_service import get_current_user
from app.database.models import User
from app.services.rag_service import rag_service
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class RagQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RagRetrieveRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

@router.post("/rag/query")
@limiter.limit("20/minute")
async def rag_query(
    request: Request,
    body: RagQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Executes a high-level query against the RAG pipeline.
    Expects to return scoring and matching category.
    """
    if not rag_service.is_loaded:
        raise HTTPException(status_code=503, detail="RAG Pipeline is currently offline.")
        
    try:
        risk_score, verdict, matched_category = rag_service.score_risk(body.query)
        return {
            "risk_score": risk_score,
            "verdict": verdict,
            "matched_category": matched_category
        }
    except Exception as e:
        logger.error(f"RAG Query error: {e}")
        raise HTTPException(status_code=500, detail="Internal RAG processing error.")

@router.post("/rag/retrieve")
@limiter.limit("30/minute")
async def rag_retrieve(
    request: Request,
    body: RagRetrieveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the top_k most similar documents from the knowledge base,
    returning full metadata and similarity scores.
    """
    if not rag_service.is_loaded:
        raise HTTPException(status_code=503, detail="RAG Pipeline is currently offline.")
        
    try:
        results = rag_service.retrieve_with_metadata(body.query, top_k=body.top_k)
        
        if not results:
            logger.warning(f"Empty retrieval for query: {body.query}")
            
        return {
            "retrieved_documents": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"RAG Retrieve error: {e}")
        raise HTTPException(status_code=500, detail="Internal RAG retrieval error.")
