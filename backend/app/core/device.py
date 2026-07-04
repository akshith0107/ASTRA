import torch
import logging

logger = logging.getLogger(__name__)

# Centralized device detection
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if DEVICE.type == "cuda":
    logger.info("Using GPU (CUDA)")
else:
    logger.info("CUDA not available. Using CPU.")

import contextlib

@contextlib.contextmanager
def safe_torch_load():
    """
    Context manager to globally patch torch.load to always inject map_location=DEVICE.
    This solves nested CUDA deserialization issues when unpickling legacy PyTorch models.
    """
    original_load = torch.load
    def _patched_load(*args, **kwargs):
        if 'map_location' not in kwargs or kwargs['map_location'] is None:
            kwargs['map_location'] = DEVICE
        return original_load(*args, **kwargs)
    
    torch.load = _patched_load
    try:
        yield
    finally:
        torch.load = original_load
