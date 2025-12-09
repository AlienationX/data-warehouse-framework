from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import typer

class BaseExecutor(ABC):
    """执行器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """建立连接"""
        pass
    
    @abstractmethod
    def execute_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """执行SQL语句"""
        pass
    
    @abstractmethod
    def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """执行查询语句"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭连接"""
        pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class ExecutorFactory:
    """执行器工厂"""
    
    @staticmethod
    def create_executor(executor_type: str, config: Dict[str, Any]) -> BaseExecutor:
        """创建执行器实例"""
        if executor_type == "hive":
            from executor.hive_executor import HiveExecutor
            return HiveExecutor(config)
        elif executor_type == "mysql":
            from executor.mysql_executor import MySQLExecutor
            return MySQLExecutor(config)
        else:
            raise ValueError(f"不支持的执行器类型: {executor_type}")