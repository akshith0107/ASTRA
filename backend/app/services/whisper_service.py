import logging
import tempfile
import os
import whisper
import torch
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhisperService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhisperService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.is_loaded = False
        return cls._instance

    def __init__(self):
        if not self.is_loaded:
            self.load_model()

    def load_model(self):
        """
        Loads the whisper model only once during startup (Singleton).
        Optimized for CPU if CUDA is not available.
        """
        logger.info(f"Loading Whisper model '{settings.WHISPER_MODEL}'...")
        try:
            from app.core.device import DEVICE
            self.model = whisper.load_model(settings.WHISPER_MODEL, device=str(DEVICE))
            self.is_loaded = True
            logger.info(f"Whisper model '{settings.WHISPER_MODEL}' loaded successfully on {DEVICE}.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.is_loaded = False

    def _save_temp_audio(self, audio_data: bytes, extension: str = ".wav") -> str:
        """
        Saves binary audio data to a temporary file for whisper decoding.
        """
        fd, temp_path = tempfile.mkstemp(suffix=extension)
        with os.fdopen(fd, 'wb') as f:
            f.write(audio_data)
        return temp_path

    async def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribes audio data to text.
        Supports standard formats via ffmpeg decoding.
        """
        import asyncio
        
        if not audio_data:
            return ""
            
        if not self.is_loaded or self.model is None:
            logger.error("Whisper model is not loaded.")
            return ""

        temp_path = self._save_temp_audio(audio_data)
        try:
            # CPU optimized inference offloaded to background thread
            def sync_transcribe():
                return self.model.transcribe(temp_path, fp16=False)
                
            result = await asyncio.to_thread(sync_transcribe)
            return result.get("text", "").strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detects the language of the audio by reading the first 30 seconds.
        """
        if not audio_data or not self.is_loaded or self.model is None:
            return "unknown"
            
        temp_path = self._save_temp_audio(audio_data)
        try:
            # load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(temp_path)
            audio = whisper.pad_or_trim(audio)

            # make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio, n_mels=self.model.dims.n_mels).to(self.model.device)

            # detect the spoken language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            return detected_lang
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "unknown"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    async def transcribe_chunk(self, audio_data: bytes) -> str:
        """
        Optimized method for transcribing live monitor audio chunks.
        """
        # For live monitoring chunks, we treat them the same as full transcriptions
        # but in a production env we might use a sliding window.
        return await self.transcribe(audio_data)

whisper_service = WhisperService()
