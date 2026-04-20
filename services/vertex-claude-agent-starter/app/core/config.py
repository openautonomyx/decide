from functools import lru_cache

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "vertex-claude-agent-starter"
    environment: str = "dev"
    log_level: str = "INFO"

    service_api_key: str = Field(min_length=16)

    google_cloud_project: str
    vertex_region: str = "us-central1"
    cloud_ml_region: str | None = None
    google_application_credentials: str
    claude_model: str = "claude-sonnet-4@20250514"

    request_timeout_seconds: float = 45.0
    max_input_chars: int = 10000
    max_turns: int = 6
    max_tool_calls: int = 6
    enabled_tools: str = "calculator,current_datetime,web_search_stub"

    enterprise_system_prompt: str = (
        "You are an enterprise assistant. Be concise, factual, and safe. "
        "Use tools when needed and never fabricate tool outputs."
    )

    @property
    def resolved_vertex_region(self) -> str:
        return self.cloud_ml_region or self.vertex_region

    @property
    def tool_allowlist(self) -> set[str]:
        return {item.strip() for item in self.enabled_tools.split(",") if item.strip()}

    @model_validator(mode="after")
    def validate_limits(self) -> "Settings":
        if self.max_turns < 1:
            raise ValueError("max_turns must be >= 1")
        if self.max_tool_calls < 0:
            raise ValueError("max_tool_calls must be >= 0")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f"Invalid configuration: {exc}") from exc
