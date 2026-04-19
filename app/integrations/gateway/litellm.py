"""
LiteLLM Model Adapter
httpx adapter for LiteLLM proxy - model routing with fallbacks
https://docs.litellm.ai/docs/proxy/configs
"""
import os
from typing import Optional, Dict, Any, List, AsyncIterator
from datetime import datetime

import httpx
from pydantic import BaseModel


class LiteLLMSettings(BaseModel):
    """LiteLLM proxy configuration."""
    base_url: str = "http://localhost:4000"
    api_key: Optional[str] = None
    timeout: float = 60.0


class ModelInfo(BaseModel):
    """Model information."""
    model_name: str
    mode: Optional[str] = None
    supports_function_calling: bool = False
    supports_vision: bool = False


class CompletionRequest(BaseModel):
    """Completion request."""
    model: str
    messages: List[Dict[str, Any]]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class CompletionResponse(BaseModel):
    """Completion response."""
    model: str
    content: str
    usage: Dict[str, int]
    finish_reason: str


class ChatMessage(BaseModel):
    """Chat message."""
    role: str
    content: str


class LiteLLMAdapter:
    """LiteLLM model adapter with fallbacks."""

    def __init__(self, settings: Optional[LiteLLMSettings] = None):
        base_url = settings.base_url if settings else os.environ.get("LITE_LLM_BASE_URL", "http://localhost:4000")
        api_key = settings.api_key if settings else os.environ.get("LITE_LLM_API_KEY", "")
        
        self._settings = LiteLLMSettings(base_url=base_url, api_key=api_key)
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=60.0,
        )

    def get_provider_name(self) -> str:
        return "litellm"

    def list_models(self) -> List[ModelInfo]:
        """List available models."""
        try:
            resp = self._client.get("/v1/model_info")
            resp.raise_for_status()
            data = resp.json().get("model_info", {})
            return [
                ModelInfo(
                    model_name=name,
                    mode=info.get("mode"),
                    supports_function_calling=info.get("supports_function_calling", False),
                    supports_vision=info.get("supports_vision", False),
                )
                for name, info in data.items()
            ]
        except httpx.HTTPError:
            return []

    def complete(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> CompletionResponse:
        """Call completion endpoint."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        try:
            resp = self._client.post("/v1/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            return CompletionResponse(
                model=data.get("model", model),
                content=data["choices"][0]["message"]["content"],
                usage=data.get("usage", {}),
                finish_reason=data["choices"][0].get("finish_reason", "stop"),
            )
        except httpx.HTTPError as e:
            raise RuntimeError(f"LiteLLM completion failed: {e}")

    def complete_with_fallback(
        self,
        models: List[str],
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> CompletionResponse:
        """Try models in order, fallback on failure."""
        last_error = None
        for model in models:
            try:
                return self.complete(model, messages, temperature, max_tokens)
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"All model fallbacks failed: {last_error}")

    def embed(self, model: str, input: str) -> List[float]:
        """Get embeddings."""
        try:
            resp = self._client.post("/v1/embeddings", json={"model": model, "input": input})
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"LiteLLM embedding failed: {e}")

    def close(self):
        self._client.close()