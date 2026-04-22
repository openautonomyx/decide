from adapters import ClaudeCodingBackend, DevstralLiteLLMBackend, GenericCodingBackend, get_coding_backend


def test_vertex_provider_routes_to_claude_backend():
    backend = get_coding_backend(
        "claude_vertex",
        {"config": {"provider": "vertex_ai", "enabled": True}},
    )
    assert isinstance(backend, ClaudeCodingBackend)


def test_vertex_transport_routes_to_claude_backend():
    backend = get_coding_backend(
        "claude_vertex",
        {"config": {"provider": "custom", "transport": "anthropic_vertex", "enabled": True}},
    )
    assert isinstance(backend, ClaudeCodingBackend)


def test_openai_compatible_transport_routes_to_litellm():
    backend = get_coding_backend(
        "local_llm",
        {"config": {"provider": "custom", "transport": "openai_compatible", "enabled": True}},
    )
    assert isinstance(backend, DevstralLiteLLMBackend)


def test_unknown_provider_routes_to_generic_backend():
    backend = get_coding_backend(
        "unknown_backend",
        {"config": {"provider": "custom", "enabled": True}},
    )
    assert isinstance(backend, GenericCodingBackend)
