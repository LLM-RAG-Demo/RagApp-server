import yaml
from dataclasses import dataclass, field
from typing import Dict
import os


@dataclass(frozen=True)
class Config:
    data: Dict = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str = '../config.yaml'):
        """
        工厂方法：从配置文件创建Config实例。
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        return cls(data=config_data)


config = Config.load()