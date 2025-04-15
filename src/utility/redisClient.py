from typing import Optional

import redis

from src.conf.config import config


class RedisClient:
    _instance: Optional['RedisClient'] = None

    def __init__(self):
        self.connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        redis_config = config.data['redis']
        self.host = redis_config['host']
        self.port = redis_config['port']
        self.password = redis_config['password']
        self.db = redis_config.get('db', 0)

    def connect(self):
        try:
            self.connection = redis.Redis(host=self.host, port=self.port, password=self.password, db=self.db)
            self.connection.ping()
        except redis.ConnectionError as e:
            print(e)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
