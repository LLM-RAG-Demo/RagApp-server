from src.dal.LLMConnector import LLMConnector


class RagService:
    def __init__(self):
        self.llm_connector = LLMConnector()

    def generate(self, query: str, conversation_id: str):
        llm = self.llm_connector.get_llm()
