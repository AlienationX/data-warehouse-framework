import logging

from core.sql_builder import SQLBuilder


class Status:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BaseTask:
    """任务基类"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "基础任务"
        self.status = "pending"
        self.enabled = True  # 默认启用, 可通过配置禁用
        self.logger = logging.getLogger(__name__)

    def create(self):
        """创建表结构"""
        return ""

    def get_sql_template(self) -> str:
        """获取SQL模板"""
        raise NotImplementedError("子类必须实现此方法")

    def validate_params(self, params) -> bool:
        """参数验证"""
        return True

    def execute(self, executor, params):
        """执行任务"""
        # 构建SQL
        sql_template = self.get_sql_template()
        sql = SQLBuilder.build_sql(sql_template, params)

        # 执行SQL
        if sql.strip().lower().startswith("select"):
            return executor.execute_query(sql)
        else:
            return executor.execute_sql(sql)

    # def insert(self):
    #     """插入数据"""

    def log(self):
        """记录日志"""

    def pre_sql(self):
        """before_execute"""
        pass

    def post_sql(self):
        """after_execute"""
        pass

    def depends(self):
        """依赖关系"""
        # TODO
        pass
