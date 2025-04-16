from typing import Optional

import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from src.conf.config import config


class MySQLClient:
    _instance: Optional['MySQLClient'] = None
    _pool: Optional[PooledDB] = None  # 定义连接池

    def __init__(self):
        self.connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MySQLClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        mysql_config = config.data['mysql']
        # 初始化连接池
        self._pool = PooledDB(
            creator=pymysql,  # 使用pymysql作为连接的创建者
            mincached=mysql_config.get('mincached', 10),  # 连接池中空闲连接的初始数量
            maxcached=mysql_config.get('maxcached', 5),# 连接池中空闲连接的最大数量
            maxshared=mysql_config.get('maxshared', 5),  # 共享连接的最大数量
            maxconnections=mysql_config.get('maxconnections', 100),  # 连接池允许的最大连接数
            blocking=True,  # 连接数达到最大时是否阻塞
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['db'],
            charset='utf8mb4',
            cursorclass=DictCursor
        )

    def connect(self):
        try:
            self.connection = self._pool.connection()  # 从连接池获取连接
            return self.connection
        except Exception as e:
            print(e)

    def close(self):
        if self.connection:
            self.connection.close()  # 归还连接到连接池
            self.connection = None