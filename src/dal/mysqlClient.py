from typing import Optional

import pymysql
from pymysql.cursors import DictCursor

from src.conf.config import config


class MySQLClient:
    _instance: Optional['MySQLClient'] = None

    def __init__(self):
        self.connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MySQLClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        mysql_config = config.data['mysql']
        self.host = mysql_config['host']
        self.port = mysql_config['port']
        self.user = mysql_config['user']
        self.password = mysql_config['password']
        self.db = mysql_config['db']

    def connet(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                charset='utf8mb4',
                cursorclass=DictCursor
            )
        except Exception as e:
            print(e)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
