"""
Autonomyx Backend Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://autonomyx:autonomyx@localhost:5432/autonomyx"
    
    # API
    api_prefix: str = "/api/v1"
    debug: bool = True
    
    # Agent Runtime
    claude_coder_url: str = "http://localhost:18080"
    memory_service_url: str = "http://localhost:18090"
    
    # LiteLLM (optional)
    lite_llm_url: str = "http://localhost:4000"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()