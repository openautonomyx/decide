import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.security import require_api_key
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.container import get_agent

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    try:
        answer, audit = await get_agent().run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatResponse(answer=answer, request_id=request.headers.get("x-request-id", ""), audit=audit)


@router.post("/stream")
async def stream_chat(payload: ChatRequest) -> StreamingResponse:
    async def sse_gen():
        try:
            async for event in get_agent().stream_run(payload):
                yield f"event: {event['type']}\n"
                yield f"data: {json.dumps(event['payload'])}\n\n"
        except ValueError as exc:
            yield "event: error\n"
            yield f"data: {json.dumps({'detail': str(exc)})}\n\n"

    return StreamingResponse(sse_gen(), media_type="text/event-stream")
