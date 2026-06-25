import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.whisper_service import whisper_service
from app.services.bert_service import bert_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing SentinelX ML Models...")
    
    try:
        # Load BERT Models
        bert_service.load_model()
        app.state.bert_service = bert_service
        
        # Load Whisper Model
        whisper_service.load_model()
        app.state.whisper_service = whisper_service
        
        # Load ChromaDB RAG Engine
        rag_service.initialize_chroma()
        app.state.rag_service = rag_service
        
        logger.info("All ML Models loaded successfully into app.state")
    except Exception as e:
        logger.error(f"Failed to load ML models during startup: {e}")
        
    yield
    
    # Shutdown logic
    logger.info("Shutting down SentinelX ML Models...")
    app.state.bert_service = None
    app.state.whisper_service = None
    app.state.rag_service = None
