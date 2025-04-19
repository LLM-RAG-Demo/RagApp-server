from typing import List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.models.message import Message
from src.service.RagService import RagService


class QueryRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    history: List[Message] | None = None

router = APIRouter()
rag_service = RagService()


@router.post("/query")
async def query(request: QueryRequest):
    message = Message(id='null', role='user', content=request.query)
    kwargs = {}
    if request.history is not None:
        kwargs['history'] = request.history

    # async for chunk in rag_service.generate(message, request.conversation_id, **kwargs):
    #     yield chunk
    # 使用 StreamingResponse 返回异步生成器
    async def stream():
        async for chunk in rag_service.generate(message, request.conversation_id, **kwargs):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")