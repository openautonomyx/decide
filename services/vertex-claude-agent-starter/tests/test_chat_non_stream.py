from app.schemas.chat import AuditLog


class FakeAgent:
    async def run(self, request):
        return "hello", AuditLog(turns=1, tool_calls=0, tools_invoked=[], model="fake")


def test_chat_non_stream(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.chat.get_agent", lambda: FakeAgent())
    resp = client.post(
        "/chat",
        headers={"x-api-key": "test-api-key-123456"},
        json={"message": "hi", "history": []},
    )
    assert resp.status_code == 200
    assert resp.json()["answer"] == "hello"
