"""
Tests for adapters module.
"""
import pytest
from adapters import (
    CodingBackend,
    ClaudeCodingBackend,
    DevstralLiteLLMBackend,
    ImageEditingBackend,
    CapabilityRouter,
)


class TestCapabilityRouter:
    """Test capability routing."""
    
    def test_get_coding_backend(self):
        """Test coding capability routes to coding adapter."""
        factory = CapabilityRouter.get_backend("coding")
        assert callable(factory)
    
    def test_get_image_editing_backend(self):
        """Test image_editing capability routes to image adapter."""
        factory = CapabilityRouter.get_backend("image_editing")
        assert callable(factory)
    
    def test_unknown_capability_defaults_to_coding(self):
        """Unknown capability defaults to coding adapter."""
        factory = CapabilityRouter.get_backend("unknown")
        assert callable(factory)
    
    def test_register_capability(self):
        """Test custom capability registration."""
        def custom_factory(backend_id, backend):
            return None
        
        CapabilityRouter.register_capability("custom", custom_factory)
        
        factory = CapabilityRouter.get_backend("custom")
        assert factory == custom_factory


class TestCodingBackend:
    """Test base CodingBackend."""
    
    def test_normalize_response(self):
        """Test response normalization."""
        backend = ClaudeCodingBackend("test", {"config": {}})
        
        result = backend._normalize_response(
            summary="test summary",
            backend_used="test_backend",
            usage={"tokens": 100},
            artifacts={"created": "file.py"},
            raw_response={"data": "test"},
        )
        
        assert result["summary"] == "test summary"
        assert result["backend_used"] == "test_backend"
        assert result["usage"] == {"tokens": 100}
        assert result["artifacts"] == {"created": "file.py"}
        assert result["raw_response"] == {"data": "test"}


class TestImageEditingBackend:
    """Test ImageEditingBackend."""
    
    def test_image_editing_stub_response(self):
        """Test image editing returns stub response."""
        backend = ImageEditingBackend(
            "gpt_image",
            {"config": {"provider": "openai", "model": "dall-e-3"}},
        )
        
        # Create a mock task
        class MockTask:
            goal = "Generate a sunset"
        
        result = backend.run(MockTask())
        
        assert result["backend_used"] == "gpt_image"
        assert result["artifacts"]["status"] == "stub"
        assert "Image editing via gpt_image" in result["summary"]