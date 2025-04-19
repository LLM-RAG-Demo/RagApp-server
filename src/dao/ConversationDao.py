import datetime
import json

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

    def add_message(self, conversation_id :str, message: Message):
        collection = self.mongo_client.db["conversation"]
        try:
            self.redis_client.connect()
            result = collection.update_one(
                {"id": conversation_id},
                {
                    "$push": {"messages": message.model_dump()},
                    "$set": {"updated_at": datetime.datetime.now()}
                }
            )
            if result.modified_count == 0:
                new_conversation = {
                    "id": conversation_id,
                    "messages": [message.model_dump()],
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
                result = collection.insert_one(new_conversation)
            self.redis_client.connection.rpush(
                f"conversation:{conversation_id}",
                message.model_dump_json()
            )
            self.redis_client.close()
            return None
        except Exception as e:
            raise ConversationDaoError(f"Error adding message to conversation: {e}") from e

    def get_last_messages(self, conversation_id :str, leng=10, redis=None):
        try:
            self.redis_client.connect()
            key = f"conversation:{conversation_id}"
            if self.redis_client.connection.exists(key):
                messages = self.redis_client.connection.lrange(key, -leng, -1)
            else:
                collection = self.mongo_client.db["conversation"]
                pipeline = [
                    {"$match": {"id": conversation_id}},
                    {"$project": {"messages": {"$slice": ["$messages", -leng]}}}
                ]
                result = list(collection.aggregate(pipeline))
                if result:
                    messages = result[0].get("messages", [])
                    self.redis_client.connection.rpush(key, *[json.dumps(msg) for msg in messages])
                else:
                    messages = []

            messages = [Message.model_validate_json(msg.decode('utf-8'))
                        if isinstance(msg, bytes) else Message.model_validate_json(msg)
                        for msg in messages]
            self.redis_client.close()
            return messages
        except Exception as e:
            raise ConversationDaoError(f"Unexpected error: {e}") from e
