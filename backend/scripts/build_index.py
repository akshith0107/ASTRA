import os
import json
import csv
import logging
import argparse
from typing import List, Dict, Any

# Ensure backend root is in PYTHONPATH
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the RagService we created
from app.services.rag_service import rag_service

# Fix Windows console encoding for pipeline.py print statements (e.g. '→')
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

JSON_DIR = os.path.join("data", "rag", "json")
CSV_DIR = os.path.join("data", "rag", "csv")

def load_json_files(directory: str) -> List[Dict[str, Any]]:
    docs = []
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist.")
        return docs
        
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        docs.extend(data)
                    else:
                        docs.append(data)
                logger.info(f"Loaded JSON file: {filename}")
            except Exception as e:
                logger.error(f"Corrupt JSON file {filename}: {e}")
    return docs

def load_csv_files(directory: str) -> List[Dict[str, Any]]:
    docs = []
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist.")
        return docs
        
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        docs.append(row)
                logger.info(f"Loaded CSV file: {filename}")
            except Exception as e:
                logger.error(f"Corrupt CSV file {filename}: {e}")
    return docs

def build_index():
    logger.info("Starting RAG Index Build...")
    
    # Load documents into dicts first
    json_docs = load_json_files(JSON_DIR)
    csv_docs = load_csv_files(CSV_DIR)
    all_raw_docs = json_docs + csv_docs
    
    logger.info(f"Total documents loaded from disk: {len(all_raw_docs)} (JSON: {len(json_docs)}, CSV: {len(csv_docs)})")
    
    if not all_raw_docs:
        logger.warning("No documents found. Exiting.")
        return
        
    try:
        import sys
        rag_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'rag'))
        if rag_dir not in sys.path:
            sys.path.append(rag_dir)
            
        from app.rag.pipeline import Document, ASTRAIndex
        from pathlib import Path
        
        # Convert raw dicts to Document objects
        docs = []
        for raw in all_raw_docs:
            text = raw.get("text", "")
            # Ensure text exists
            if not text:
                continue
            # Pass all fields except text as metadata
            metadata = {k: v for k, v in raw.items() if k != "text"}
            # The pipeline.py expects a "label" (scam/legitimate) and "category"
            if "label" not in metadata:
                metadata["label"] = "scam"
            docs.append(Document(text=text, metadata=metadata))
            
        logger.info(f"Converted {len(docs)} raw entries into Document objects.")
        
        # Build Index
        index = ASTRAIndex()
        index.build(docs)
        
        # Save Index
        index.save(Path(rag_dir))
        logger.info(f"Successfully saved index.pkl to {rag_dir}.")
            
    except Exception as e:
        logger.error(f"Embedding or indexing failure: {e}")

if __name__ == "__main__":
    build_index()
