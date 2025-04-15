import unittest
from unittest.mock import patch
from src.dal.redisClient import RedisClient
import redis
from src.conf.config import config

class TestRedisClient(unittest.TestCase):

    def setUp(self):
        # 模拟配置
        self.mock_config = {
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': 'redis'
            }
        }
        with patch.dict(config.data, self.mock_config):
            self.redis_client = RedisClient()

    @patch('redis.Redis')
    def test_connect_success(self, mock_redis):
        # 模拟连接成功
        mock_redis.return_value.ping.return_value = True

        self.redis_client.connect()

        # 验证 Redis 是否被正确初始化
        mock_redis.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            password='redis',
        )
        # 验证 ping 方法是否被调用
        mock_redis.return_value.ping.assert_called_once()

    @patch('redis.Redis')
    def test_connect_failure(self, mock_redis):
        # 模拟连接失败
        mock_redis.side_effect = redis.ConnectionError("Connection failed")

        with self.assertLogs(level='INFO') as log:
            self.redis_client.connect()

        # 验证日志输出
        self.assertIn("Error connecting to Redis: Connection failed", log.output[0])

    @patch('redis.Redis')
    def test_close(self, mock_redis):
        # 模拟连接成功
        mock_redis.return_value.ping.return_value = True
        self.redis_client.connect()

        # 关闭连接
        self.redis_client.close()

        # 验证连接是否被关闭
        self.assertIsNone(self.redis_client.connection)


if __name__ == '__main__':
    unittest.main()
