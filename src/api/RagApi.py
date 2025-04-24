import asyncio
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.pojo import Message
from src.service import use_chat_service


class QueryRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    history: List[Message] | None = None

router = APIRouter()


@router.post("/query")
async def query(request: QueryRequest, chat_service=Depends(use_chat_service)):
    message = Message(id='null', role='user', content=request.query)
    kwargs = {}
    if request.history is not None:
        kwargs['history'] = request.history

    async def stream():
        # 发送初始心跳，确保连接已建立
        yield ":\n\n"  # 这是 SSE 的注释格式，客户端会忽略

        async for chunk in chat_service.generate(message, request.conversation_id, **kwargs):
            # 确保有空格: "data: "，而不是 "data:"
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.01)  # 强制让出更长时间

        # 结束时发送一个完成信号
        yield f"data: [DONE]\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
    )
