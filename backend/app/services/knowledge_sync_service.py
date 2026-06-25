import logging
import uuid
from typing import Optional
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class KnowledgeSyncService:
    def sync_campaign_to_chroma(self, text: str, campaign_name: str, scam_type: str, document_id: Optional[str] = None):
        """
        Syncs a campaign artifact or transcript to ChromaDB for RAG intelligence.
        """
        doc_id = document_id or str(uuid.uuid4())
        try:
            rag_service.add_document(
                doc_id=doc_id,
                text=text,
                campaign_name=campaign_name,
                scam_type=scam_type
            )
            logger.info(f"Successfully synced campaign {campaign_name} to ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to sync knowledge to ChromaDB: {e}")

knowledge_sync_service = KnowledgeSyncService()
