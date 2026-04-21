"""
Autonomyx Backend Configuration
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


Environment = Literal["local", "dev", "staging", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # App identity
    project_name: str = "Autonomyx API"
    app_version: str = "1.0.0"
    environment: Environment = "local"

    # Database / cache
    database_url: str = "postgresql://autonomyx:autonomyx@localhost:5432/autonomyx"
    redis_url: str = "redis://localhost:6379"

    # API
    api_prefix: str = "/api/v1"
    debug: bool = False
    log_level: str = "INFO"

    # Networking
    allowed_origins: List[str] = Field(default_factory=list)
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])

    # Agent runtime
    claude_coder_url: str = "http://localhost:18080"
    memory_service_url: str = "http://localhost:18090"

    # LiteLLM (optional)
    lite_llm_url: str = "http://localhost:4000"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    # Operations
    seed_on_startup: bool = False

    @field_validator("allowed_origins", "allowed_hosts", mode="before")
    @classmethod
    def parse_csv_or_list(cls, value):
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        raise TypeError(f"Unsupported list value: {type(value)!r}")

    @model_validator(mode="after")
    def validate_security(self):
        insecure_default = self.secret_key == "dev-secret-key-change-in-production"

        if self.environment in {"staging", "prod"} and insecure_default:
            raise ValueError("SECRET_KEY must be overridden outside local development.")

        if self.environment == "prod" and self.debug:
            raise ValueError("DEBUG must be false in production.")

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()
