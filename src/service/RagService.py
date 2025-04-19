import json

from snowflake import SnowflakeGenerator

from src.dal.LLMConnector import LLMConnector
from src.dao.ConversationDao import ConversationDao
from src.models.message import Message

from langchain.schema import HumanMessage, AIMessage, SystemMessage


class RagService:
    def __init__(self):
        self.llm_connector = LLMConnector()
        self.conversation_dao = ConversationDao()
        self.conversation_gen = SnowflakeGenerator(1)
        self.message_gen = SnowflakeGenerator(2)

    async def generate(self, query: Message, conversation_id: str, **kwargs):
        llm = await self.llm_connector.get_llm()
        # handler = llm.callbacks[0]
        if conversation_id is None:
            conversation_id = str(next(self.conversation_gen))
        if query.id == 'null':
            query.id = str(next(self.message_gen))
        history = kwargs.get('history', [])
        if not history:
            history = self.conversation_dao.get_last_messages(conversation_id)

        messages = []
        for msg in history:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))
            else:
                messages.append(SystemMessage(content=msg.content))
        messages.append(HumanMessage(content=query.content))

        response = ''
        async for chunk in llm.astream(messages):
            yield chunk.content
            response += chunk.content
        # task = asyncio.create_task(llm.agenerate([messages]))
        # async for token in handler.aiter():
        #     print(token, end='', flush=True)
        #     response += token
        #     yield token
        #     await asyncio.sleep(0)
        # await task

        yield json.dumps({'code': 200, 'conversation_id': conversation_id})

        self.conversation_dao.add_message(conversation_id, query)
        self.conversation_dao.add_message(conversation_id, Message(id=str(next(self.message_gen)),role='assistant', content=response))
