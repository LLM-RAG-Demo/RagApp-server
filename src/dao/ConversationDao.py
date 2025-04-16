from src.dal.MongoClient import MongoDBClient
from src.dal.RedisClient import RedisClient
from src.models.message import Message


class ConversationDao:
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.redis_client = RedisClient()

    def add_message(self, conversation_id, message: Message):
        collection = self.mongo_client.db["conversation"]
        try:
            result = collection.update_one(
                {"_id": conversation_id},
                {"$push": {"messages": message.model_dump()}}
            )
        except Exception as e:
            print(f"Error adding message to conversation: {e}")
            return False

    def get_last_messages(self, conversation_id, len = 10):
        try:
            messages = self.redis_client.connection.lrange(f"conversation:{conversation_id}", -len, -1)
            messages =