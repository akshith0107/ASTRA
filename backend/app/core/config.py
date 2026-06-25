from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelX"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sentinelx.db"
    
    # JWT
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM
    GROQ_API_KEY: str = ""
    
    # Whisper
    WHISPER_MODEL: str = "tiny"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Model Paths
    BERT_MODEL_PATH: str = "app/models/bert/bert_model.pkl"
    LABEL_ENCODER_PATH: str = "app/models/bert/label_encoder.pkl"
    TOKENIZER_PATH: str = "app/models/bert/tokenizer.pkl"
    
    class Config:
        env_file = ".env"

settings = Settings()
