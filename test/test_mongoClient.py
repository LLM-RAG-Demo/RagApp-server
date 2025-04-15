import unittest
from unittest.mock import patch

from src.dal.MongoClient import MongoDBClient
from src.conf.config import config

class TestMongoDBClient(unittest.TestCase):

    @patch('src.utility.mongoClient.MongoClient')
    def test_singleton_instance(self, mock_mongo_client):
        # 第一次实例化
        instance1 = MongoDBClient()
        # 第二次实例化
        instance2 = MongoDBClient()

        # 验证两次实例化返回的是同一个对象
        self.assertIs(instance1, instance2)

    @patch('src.utility.mongoClient.MongoClient')
    def test_initialization(self, mock_mongo_client):
        # 模拟配置
        mock_config = {
            'mongo': {
                'host': 'localhost',
                'port': 27017,
                'db': 'test-db'
            }
        }
        with patch.dict(config.data, mock_config):
            # 配置 __getitem__ 返回的对象的 name 属性
            mock_mongo_client.return_value.__getitem__.return_value.name = 'test-db'

            instance = MongoDBClient()

            # 验证 MongoClient 是否被正确初始化
            mock_mongo_client.assert_called_once_with('localhost', 27017)
            # 验证数据库是否被正确设置
            self.assertEqual(instance.db.name, 'test-db')

if __name__ == '__main__':
    unittest.main()