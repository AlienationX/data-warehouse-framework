from pathlib import Path

import yaml


class Config:
    """配置管理类"""

    def __init__(self):
        self.default_executor = "hive"
        self.executors = {
            "hive": {
                "class": "executor.hive_executor.HiveExecutor",
                "config": {"host": "localhost", "port": 10000, "database": "default"},
            },
            "spark": {
                "class": "executor.hive_executor.SparkExecutor",
                "config": {
                    "host": "localhost",
                    "port": 10000,
                    "database": "default",
                    "user": "spark_user",
                    "password": "spark_password",
                },
            },
            "mysql": {
                "class": "executor.mysql_executor.MySQLExecutor",
                "config": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "data_warehouse",
                    "user": "root",
                    "password": "password",
                },
            },
            "postgresql": {
                "class": "executor.postgresql_executor.PostgreSQLExecutor",
                "config": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "data_warehouse",
                    "user": "postgres",
                    "password": "password",
                },
            },
        }

    def load_from_file(self, config_path: Path) -> None:
        """从YAML文件加载配置"""
        if config_path.exists():
            with open(config_path, "r") as f:
                external_config = yaml.safe_load(f)
                self.executors.update(external_config.get("executors", {}))


config = Config()
