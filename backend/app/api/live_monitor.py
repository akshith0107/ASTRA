import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.indicator_service import indicator_service
from app.services.risk_engine import risk_engine

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

from jose import jwt, JWTError
from app.core.config import settings

@router.websocket("/ws/live-monitor")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for live audio monitoring.
    Expects binary audio chunks, processes them through the intelligence pipeline,
    and returns a JSON payload with transcript, score, and indicators.
    """
    if not token:
        await websocket.close(code=1008)
        return
        
    try:
        # Validate JWT Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return
        
    await manager.connect(websocket)
    try:
        whisper_service = websocket.app.state.whisper_service
        bert_service = websocket.app.state.bert_service
        
        while True:
            # Receive audio frame (binary)
            audio_data = await websocket.receive_bytes()
            
            # Step 1: Whisper Transcription
            transcript = await whisper_service.transcribe_chunk(audio_data)
            
            if transcript.strip():
                # Step 2: BERT Classification
                scam_type, confidence = await bert_service.classify(transcript)
                
                # Step 3: Extract Indicators
                indicators = indicator_service.extract_indicators(transcript)
                
                # Step 4: Calculate Risk Score
                risk_score, risk_level = risk_engine.calculate_risk(
                    base_confidence=confidence if scam_type != "Legitimate" else 0.0,
                    indicators=indicators
                )
                
                # Format payload for frontend
                payload = {
                    "transcript": transcript,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "scam_type": scam_type,
                    "indicators": [ind.model_dump() for ind in indicators]
                }
                
                # Step 5: Push Updates
                await manager.send_personal_message(json.dumps(payload), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Live monitor client disconnected")
    except Exception as e:
        logger.error(f"Error in live-monitor websocket: {e}")
        manager.disconnect(websocket)
