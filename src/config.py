"""Configuration management for NOVA AI"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Google Gemini
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Anthropic
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/nova.db")
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/chroma")
    
    # Voice
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1024"))
    voice_threshold: float = float(os.getenv("VOICE_THRESHOLD", "0.5"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "./logs")
    
    # Debug
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    enable_voice_auth: bool = os.getenv("ENABLE_VOICE_AUTH", "True").lower() == "true"
    security_level: int = int(os.getenv("SECURITY_LEVEL", "2"))
    voice_auth_threshold: float = float(os.getenv("VOICE_AUTH_THRESHOLD", "0.85"))
    voice_samples_dir: str = os.getenv("VOICE_SAMPLES_DIR", "./data/voice_samples")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
