from typing import Optional

from pymongo import MongoClient

from src.conf.config import config


class MongoDBClient:
    _instance: Optional['MongoDBClient'] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDBClient, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        mongo_config = config.data['mongo']
        self.client = MongoClient(mongo_config['host'], mongo_config['port'])
        self.db = self.client[mongo_config['db']]
