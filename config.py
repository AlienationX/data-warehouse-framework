from typing import Dict, Any, Optional
from pathlib import Path
import yaml

class Config:
    """配置管理类"""
    def __init__(self):
        self.default_executor = "hive"
        self.executors = {
            "hive": {
                "class": "executor.hive_executor.HiveExecutor",
                "config": {
                    "host": "localhost",
                    "port": 10000,
                    "database": "default"
                }
            },
            "mysql": {
                "class": "executor.mysql_executor.MySQLExecutor",
                "config": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "password",
                    "database": "data_warehouse"
                }
            }
        }
    
    def load_from_file(self, config_path: Path) -> None:
        """从YAML文件加载配置"""
        if config_path.exists():
            with open(config_path, 'r') as f:
                external_config = yaml.safe_load(f)
                self.executors.update(external_config.get('executors', {}))

config = Config()