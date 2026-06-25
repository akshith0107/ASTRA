import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self):
        # Regex patterns
        self.patterns = {
            "phone": r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}",
            "upi": r"([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{3,64})",
            "url": r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
            "email": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        }

    def extract_all(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts all recognized entities from the provided text.
        Returns a list of dictionaries: [{"type": "phone", "value": "+1-800..."}, ...]
        """
        entities = []
        if not text:
            return entities
            
        for entity_type, pattern in self.patterns.items():
            matches = set(re.findall(pattern, text))
            for match in matches:
                # Handle tuples from grouped regex
                if isinstance(match, tuple):
                    match = match[0]
                if match and match.strip():
                    entities.append({"type": entity_type, "value": match.strip()})
                    
        return entities

entity_extractor = EntityExtractor()
