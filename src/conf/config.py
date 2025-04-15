import yaml
import os

class Config:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.config_data = self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        return config_data

class MongoConfig:
    def __init__(self, config: Config):
        self.config = config

    @property
    def host(self):
        return self.config.config_data['mongo']['host']

    @property
    def port(self):
        return self.config.config_data['mongo']['port']

    @property
    def db(self):
        return self.config.config_data['mongo']['db']

    @property
    def user(self):
        return self.config.config_data['mongo']['user']

    @property
    def password(self):
        return self.config.config_data['mongo']['password']