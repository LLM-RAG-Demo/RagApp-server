import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.dao.ConversationDao import ConversationDao
from src.pojo.message import Message
from src.pojo.conversation import Conversation


@pytest.fixture
def conversation_dao():
    with patch('src.dao.ConversationDao.MongoDBClient') as mock_mongo, \
         patch('src.dao.ConversationDao.RedisClient') as mock_redis:
        mock_mongo_instance = MagicMock()
        mock_redis_instance = MagicMock()
        mock_mongo.return_value = mock_mongo_instance
        mock_redis.return_value = mock_redis_instance
        return ConversationDao()


def test_add_message_new_conversation(conversation_dao):
    # 准备测试数据
    conversation_id = 1
    message = Message(id=1, content="测试消息", role="user")
    mock_collection = MagicMock()
    conversation_dao.mongo_client.db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = None
    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = 1
    mock_collection.insert_one.return_value = mock_insert_result

    # 执行测试方法
    result = conversation_dao.add_message(conversation_id, message)

    # 断言
    assert result is True
    mock_collection.insert_one.assert_called_once_with({
        "_id": conversation_id,
        "messages": [message.model_dump()],
        "created_at": pytest.approx(datetime.now(), rel=1e-2),
        "updated_at": pytest.approx(datetime.now(), rel=1e-2)
    })


def test_add_message_existing_conversation(conversation_dao):
    # 准备测试数据
    conversation_id = 1
    message = Message(id=1, content="测试消息", role="user")
    mock_collection = MagicMock()
    conversation_dao.mongo_client.db.__getitem__.return_value = mock_collection
    mock_collection.find_one.return_value = {
        "_id": conversation_id,
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1
    mock_collection.update_one.return_value = mock_update_result

    # 执行测试方法
    result = conversation_dao.add_message(conversation_id, message)

    # 断言
    assert result is True
    mock_collection.update_one.assert_called_once_with(
        {"_id": conversation_id},
        {
            "$push": {"messages": message.model_dump()},
            "$set": {"updated_at": pytest.approx(datetime.now(), rel=1e-2)}
        }
    )


def test_get_last_messages(conversation_dao):
    # 准备测试数据
    conversation_id = 1
    length = 10
    mock_messages = [b'{"content": "消息1", "sender": "user"}', b'{"content": "消息2", "sender": "user"}']
    conversation_dao.redis_client.connection.lrange.return_value = mock_messages

    # 执行测试方法
    result = conversation_dao.get_last_messages(conversation_id, length)

    # 断言
    assert len(result) == 2
    conversation_dao.redis_client.connection.lrange.assert_called_once_with(
        f"conversation:{conversation_id}", -length, -1
    )