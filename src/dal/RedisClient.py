from typing import Optional

import redis
from redis import ConnectionPool

from src.conf.config import config


class RedisClient:
    _instance: Optional['RedisClient'] = None
    _pool: Optional[ConnectionPool] = None  # 新增连接池属性

    def __init__(self):
        self.connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        redis_config = config.data['redis']
        # 初始化连接池，添加连接数量相关配置
        self._pool = ConnectionPool(
            host=redis_config['host'],
            port=redis_config['port'],
            password=redis_config['password'],
            db=redis_config.get('db', 0),
            max_connections=redis_config.get('max_connections', 10),  # 连接池允许的最大连接数，默认 10
        )

    def connect(self):
        try:
            # 从连接池获取连接
            self.connection = redis.Redis(connection_pool=self._pool)
            self.connection.ping()
        except redis.ConnectionError as e:
            print(e)

    def close(self):
        if self.connection:
            # 归还连接到连接池，这里的 close 方法只是释放连接，不是关闭连接池
            self.connection.close()
            self.connection = None