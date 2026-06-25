import logging
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import analyze, audio, dashboard, network, live_monitor
from app.database.database import Base, engine, get_db
from sqlalchemy.orm import Session

from app.core.startup import lifespan
from app.core.logging import setup_logging, request_id_ctx_var
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uuid
from starlette.requests import Request

# Setup basic logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="SentinelX API",
        description="Scam Intelligence Platform",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda req, exc: Response(content="Rate limit exceeded", status_code=429))
    app.add_middleware(SlowAPIMiddleware)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For MVP, allow all
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Health"])
    def health_check(request: Request):
        try:
            whisper_loaded = request.app.state.whisper_service.is_loaded
        except:
            whisper_loaded = False
            
        try:
            bert_loaded = request.app.state.bert_service.model is not None
        except:
            bert_loaded = False
            
        return {
            "status": "healthy",
            "api": True,
            "bert": bert_loaded,
            "whisper": whisper_loaded
        }
        
    @app.get("/ready", tags=["Health"])
    def readiness_check(request: Request, db: Session = Depends(get_db)):
        try:
            db.execute("SELECT 1")
            db_status = True
        except:
            db_status = False
            
        return {
            "status": "ready" if db_status else "not_ready",
            "database": db_status
        }

    # Include routers
    app.include_router(analyze.router, prefix=settings.API_V1_STR, tags=["Analysis"])
    app.include_router(audio.router, prefix=settings.API_V1_STR, tags=["Audio Intelligence"])
    app.include_router(dashboard.router, prefix=settings.API_V1_STR, tags=["Dashboard"])
    app.include_router(network.router, prefix=settings.API_V1_STR, tags=["Network Intelligence"])
    app.include_router(live_monitor.router, tags=["Live Monitor WebSockets"])
    from app.api import auth
    app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])

    @app.get("/")
    def read_root():
        return {"status": "SentinelX API Active"}

    return app

app = create_app()
