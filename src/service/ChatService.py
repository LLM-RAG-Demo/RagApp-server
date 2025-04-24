import json
import time

from snowflake import SnowflakeGenerator

from src.dal import use_llm
from src.dao import ConversationDao
from src.pojo import Message

from langchain.schema import HumanMessage, AIMessage, SystemMessage
from fastapi import Depends

class ChatService:
    def __init__(self, conversation_dao: ConversationDao, llm):
        print("RagService初始化")
        self.conversation_dao = conversation_dao
        self.llm = llm
        self.conversation_gen = SnowflakeGenerator(1)
        self.message_gen = SnowflakeGenerator(2)

    async def generate(self, query: Message, conversation_id: str, **kwargs):
        # handler = llm.callbacks[0]
        if conversation_id is None:
            conversation_id = str(next(self.conversation_gen))
        if query.id == 'null':
            query.id = str(next(self.message_gen))
        history = kwargs.get('history', [])
        if not history:
            history = await self.conversation_dao.get_last_messages(conversation_id)

        # 使用列表推导式转换历史消息
        messages = [
            HumanMessage(content=msg.content) if msg.role == 'user' else
            AIMessage(content=msg.content) if msg.role == 'assistant' else
            SystemMessage(content=msg.content)
            for msg in history
        ]
        # 添加当前查询消息
        messages.append(HumanMessage(content=query.content))

        astream_start = time.time()
        is_first_chunk = True

        response = ''
        async for chunk in self.llm.astream(messages):
            if is_first_chunk:
                astream_end = time.time()
                print(f"获取LLM流式响应耗时: {astream_end - astream_start} 秒")
                is_first_chunk = False
            yield json.dumps({'code': 1, 'content': chunk.content})
            response += chunk.content
        # task = asyncio.create_task(llm.agenerate([messages]))
        # async for token in handler.aiter():
        #     print(token, end='', flush=True)
        #     response += token
        #     yield token
        #     await asyncio.sleep(0)
        # await task

        yield json.dumps({'code': 100, 'status': 200, 'conversation_id': conversation_id})

        await  self.conversation_dao.add_message(conversation_id, query)
        await  self.conversation_dao.add_message(conversation_id, Message(id=str(next(self.message_gen)),role='assistant', content=response))


def use_chat_service(conversation_dao: ConversationDao = Depends(), llm=Depends(use_llm)):
    return ChatService(conversation_dao, llm)
