import unittest
from unittest.mock import patch, MagicMock

import pymysql
from pymysql.cursors import DictCursor

from src.dal.MysqlClient import MySQLClient
from src.conf.config import config

class TestMySQLClient(unittest.TestCase):

    def setUp(self):
        # 模拟配置
        self.mock_config = {
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'user': 'test_user',
                'password': 'test_password',
                'db': 'test_db'
            }
        }
        with patch.dict(config.data, self.mock_config):
            self.mysql_client = MySQLClient()

    @patch('pymysql.connect')
    def test_connet(self, mock_connect):
        # 模拟连接成功
        mock_connect.return_value = MagicMock()

        self.mysql_client.connet()

        # 验证 pymysql.connect 是否被正确调用
        mock_connect.assert_called_once_with(
            host='localhost',
            port=3306,
            user='test_user',
            password='test_password',
            db='test_db',
            charset='utf8mb4',
            cursorclass=DictCursor
        )

    @patch('pymysql.connect')
    def test_connet_exception(self, mock_connect):
        # 模拟连接失败
        mock_connect.side_effect = pymysql.MySQLError("Connection failed")

        with self.assertLogs(level='INFO') as log:
            self.mysql_client.connet()

        # 验证日志输出
        self.assertIn("Connection failed", log.output[0])

    @patch('pymysql.connect')
    def test_close(self, mock_connect):
        # 模拟连接成功
        mock_connect.return_value = MagicMock()
        self.mysql_client.connet()

        # 关闭连接
        self.mysql_client.close()

        # 验证连接是否被关闭
        self.assertIsNone(self.mysql_client.connection)

if __name__ == '__main__':
    unittest.main()
