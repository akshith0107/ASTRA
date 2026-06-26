import torch
import torch.nn.functional as F
import pickle
import os
import logging
from app.models.lstm.model import BiLSTMModel

logger = logging.getLogger(__name__)

class BiLSTMPredictor:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.device = torch.device("cpu") # Keep inference lightweight on CPU
        self.model = None
        self.vocab = None
        
        self.vocab_size = 1180
        self.embedding_dim = 128
        self.hidden_dim = 128
        self.max_length = 100 # Safe truncation
        
    def load(self):
        try:
            # 1. Load Vocab
            vocab_path = os.path.join(self.model_dir, "vocab.pkl")
            if not os.path.exists(vocab_path):
                raise FileNotFoundError(f"Vocabulary missing at {vocab_path}")
                
            with open(vocab_path, "rb") as f:
                self.vocab = pickle.load(f)
                
            # 2. Load Model
            model_path = os.path.join(self.model_dir, "bilstm_model.pth")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model missing at {model_path}")
                
            self.model = BiLSTMModel(
                vocab_size=self.vocab_size,
                embedding_dim=self.embedding_dim,
                hidden_dim=self.hidden_dim
            )
            
            # Use weights_only=True for security if using modern PyTorch, 
            # but standard load is safer for older cross-compat if needed.
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            
            # CRITICAL: Evaluation mode + remove gradients
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("BiLSTM model and vocabulary successfully loaded.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load BiLSTM model: {e}")
            self.model = None
            self.vocab = None
            return False

    def preprocess(self, text: str) -> torch.Tensor:
        """Tokenize based on exactly how train_df was parsed."""
        if not self.vocab:
            raise ValueError("Vocabulary not loaded")
            
        words = text.lower().split()
        
        # OOV tokens get mapped to <UNK> (index 1)
        # Pad token is <PAD> (index 0)
        unk_idx = self.vocab.get("<UNK>", 1)
        indices = [self.vocab.get(w, unk_idx) for w in words]
        
        # Truncate
        if len(indices) > self.max_length:
            indices = indices[:self.max_length]
            
        # If empty (e.g. all punctuation stripped out, though split() is robust)
        if len(indices) == 0:
            indices = [unk_idx]
            
        return torch.tensor([indices], dtype=torch.long, device=self.device)

    def predict(self, text: str) -> tuple[float, float]:
        """
        Returns (scam_probability, raw_confidence)
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")
            
        tensor = self.preprocess(text)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            # outputs shape: (1, 2)
            probs = F.softmax(outputs, dim=1)
            
            # Assuming index 1 is "scam" (label 1) and index 0 is "legitimate" (label 0)
            scam_prob = probs[0, 1].item()
            
            # Confidence is just the max probability selected
            confidence = probs.max().item()
            
            return scam_prob, confidence
