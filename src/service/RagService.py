from snowflake import SnowflakeGenerator

from src.dal.LLMConnector import LLMConnector
from src.dao.ConversationDao import ConversationDao
from src.models.message import Message


class RagService:
    def __init__(self):
        self.llm_connector = LLMConnector()
        self.conversation_dao = ConversationDao()
        self.snowflake_gen = SnowflakeGenerator(1)

    def generate(self, query: Message, conversation_id: str, **kwargs):
        llm = self.llm_connector.get_llm()
        if conversation_id is None:
            conversation_id = next(self.snowflake_gen)
        history = kwargs.get('history', [])
        if not history:
            history = self.conversation_dao.get_last_messages(conversation_id)

