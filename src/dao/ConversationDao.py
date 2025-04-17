import datetime

from src.dal.MongoClient import MongoDBClient
from src.dal.RedisClient import RedisClient
from src.models.message import Message

class ConversationDaoError(Exception):
    """ConversationDao 相关操作的自定义异常"""
    pass


class ConversationDao:
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.redis_client = RedisClient()

    def add_message(self, conversation_id, message: Message):
        collection = self.mongo_client.db["conversation"]
        try:
            result = collection.update_one(
                {"_id": conversation_id},
                {
                    "$push": {"messages": message.model_dump()},
                    "$set": {"updated_at": datetime.datetime.now()}
                }
            )
            if result.modified_count == 0:
                new_conversation = {
                    "_id": conversation_id,
                    "messages": [message.model_dump()],
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
                result = collection.insert_one(new_conversation)
                return True
            self.redis_client.connection.rpush(f"conversation:{conversation_id}", message.model_dump())
        except Exception as e:
            raise ConversationDaoError(f"Error adding message to conversation: {e}") from e

    def get_last_messages(self, conversation_id, len = 10):
        try:
            if self.redis_client.connection.exists(conversation_id):
                messages = self.redis_client.connection.lrange(f"conversation:{conversation_id}", -len, -1)
            else:
                collection = self.mongo_client.db["conversation"]
                pipline = [
                    {"$match": {"_id": conversation_id}},
                    {"$project": {"messages": {"$slice": ["$messages", -len]}}}
                ]
                result = collection.aggregate(pipline)
                messages = result.next().get("messages", [])
                self.redis_client.connection.rpush(f"conversation:{conversation_id}", *messages)

            messages = [Message.model_validate_json(msg.decode('utf-8'))
                                if isinstance(msg,bytes) else Message.model_validate_json(msg)
                        for msg in messages]

            return messages
        except Exception as e:
            raise ConversationDaoError(f"Error getting last messages from conversation: {e}") from e
