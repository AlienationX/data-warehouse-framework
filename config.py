import os
from collections import ChainMap
from pathlib import Path

import yaml
from decouple import Config, RepositoryEnv

# 读取环境变量，没有设置时，默认使用prod环境。本机设置为dev：export DWF_ENV=dev
# vim ~/.bash_profile
# export DWF_ENV=dev
ENV = os.getenv("DWF_ENV", "prod")
config = Config(ChainMap(RepositoryEnv(f".env.{ENV}"), RepositoryEnv(".env")))

# print("*" * 20, config)
# print("*" * 20, config.repository)
# print("*" * 20, config("DEBUG"))
# print("*" * 20, config("SECRET_KEY"))


class Config:
    """配置管理类"""

    def __init__(self):
        self.default_executor = "hive"
        self.executors = {
            "hive": {
                "class": "executor.hive_executor.HiveExecutor",
                "config": {
                    "host": config("HIVE_HOST", default="localhost"),
                    "port": config("HIVE_PORT", default=10000, cast=int),
                    "database": config("HIVE_DBNAME", default="default"),
                    "user": config("HIVE_USER", default="hive_user"),
                    "password": config("HIVE_PASSWORD", default="hive_password"),
                },
            },
            "spark": {
                "class": "executor.hive_executor.SparkExecutor",
                "config": {
                    "host": config("SPARK_HOST", default="localhost"),
                    "port": config("SPARK_PORT", default=10000, cast=int),
                    "database": config("SPARK_DBNAME", default="default"),
                    "user": config("SPARK_USER", default="spark_user"),
                    "password": config("SPARK_PASSWORD", default="spark_password"),
                },
            },
            "mysql": {
                "class": "executor.mysql_executor.MySQLExecutor",
                "config": {
                    "host": config("MYSQL_HOST", default="localhost"),
                    "port": config("MYSQL_PORT", default=3306, cast=int),
                    "database": config("MYSQL_DBNAME", default="data_warehouse"),
                    "user": config("MYSQL_USER", default="root"),
                    "password": config("MYSQL_PASSWORD", default="password"),
                },
            },
            "postgresql": {
                "class": "executor.postgresql_executor.PostgreSQLExecutor",
                "config": {
                    "host": config("POSTGRESQL_HOST", default="localhost"),
                    "port": config("POSTGRESQL_PORT", default=5432, cast=int),
                    "database": config("POSTGRESQL_DBNAME", default="data_warehouse"),
                    "user": config("POSTGRESQL_USER", default="postgres"),
                    "password": config("POSTGRESQL_PASSWORD", default="password"),
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
