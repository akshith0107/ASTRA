import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
# Stub out SentenceTransformers for testing if not fully loaded yet
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # Initialize ChromaDB local client
        self.chroma_client = chromadb.Client(Settings(is_persistent=True, persist_directory="./chroma_db"))
        
        # Load SentenceTransformer model
        if SentenceTransformer:
            logger.info("Loading SentenceTransformer model for embeddings...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            logger.warning("SentenceTransformer not found. Using stub embeddings.")
            self.model = None

        # Get or create the collection for scam knowledge base
        self.collection = self.chroma_client.get_or_create_collection(name="scam_knowledge_base")

    def create_embeddings(self, text: str) -> List[float]:
        """
        Creates vector embeddings for the given text.
        """
        if self.model:
            return self.model.encode(text).tolist()
        else:
            # Return dummy embedding if model isn't available
            return [0.0] * 384

    def add_document(self, doc_id: str, text: str, campaign_name: str, scam_type: str):
        """
        Adds a new scam script/report to the ChromaDB collection.
        """
        embedding = self.create_embeddings(text)
        
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"campaign_name": campaign_name, "scam_type": scam_type}],
            ids=[doc_id]
        )
        logger.info(f"Added document {doc_id} to scam_knowledge_base")

    def similarity_search(self, text: str, n_results: int = 1) -> Dict[str, Any]:
        """
        Searches the ChromaDB collection for similar text.
        """
        embedding = self.create_embeddings(text)
        
        if self.collection.count() == 0:
            return {"distances": [[]], "metadatas": [[]], "documents": [[]]}

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(n_results, self.collection.count())
        )
        return results

    def retrieve_similar_scams(self, text: str, threshold_distance: float = 1.0) -> Tuple[str, float, str]:
        """
        Retrieves the most similar scam campaign and returns its details.
        Returns: campaign_name, similarity_score, scam_type
        """
        results = self.similarity_search(text, n_results=1)
        
        if not results['distances'][0]:
            return None, 0.0, None

        distance = results['distances'][0][0]
        # Invert distance to get a similarity score (closer to 0 distance = 1.0 similarity)
        # Using a simple conversion for L2 distance (or cosine distance depending on chroma setup)
        similarity_score = max(0.0, 1.0 - (distance / 2.0))
        
        if similarity_score < 0.5: # Example threshold
            return None, similarity_score, None
            
        metadata = results['metadatas'][0][0]
        
        return metadata.get('campaign_name'), similarity_score, metadata.get('scam_type')

rag_service = RAGService()
