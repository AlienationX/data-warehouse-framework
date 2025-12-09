from typing import Dict, Any, Optional
from core.sql_builder import SQLBuilder

class BaseTask:
    """任务基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "基础任务"
    
    def get_sql_template(self) -> str:
        """获取SQL模板"""
        raise NotImplementedError("子类必须实现此方法")
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """参数验证"""
        return True
    
    def execute(self, executor, params: Dict[str, Any]) -> Any:
        """执行任务"""
        # 构建SQL
        sql_template = self.get_sql_template()
        sql = SQLBuilder.build_sql(sql_template, params)
        
        # 执行SQL
        if sql.strip().lower().startswith('select'):
            return executor.execute_query(sql)
        else:
            return executor.execute_sql(sql)

class Task(BaseTask):
    """ODS层任务1示例"""
    
    def __init__(self):
        super().__init__()
        self.description = "ODS用户数据清洗任务"
    
    def get_sql_template(self) -> str:
        return """
        INSERT INTO ods.user_clean
        SELECT 
            user_id,
            user_name,
            email,
            /* IF enable_phone_mask */ 
            mask(phone) as phone,
            /* ELSE */
            phone,
            /* ENDIF */
            create_time
        FROM source.user_data 
        WHERE create_time >= '${start_date}' 
          AND create_time < '${end_date}'
          /* IF user_type */
          AND user_type = '${user_type}'
          /* ENDIF */
        """
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        required = ['start_date', 'end_date']
        for field in required:
            if field not in params:
                raise ValueError(f"缺少必要参数: {field}")
        return True

# 兼容函数式任务定义
def main(executor, params: Dict[str, Any]) -> Any:
    """函数式任务定义示例"""
    task = Task()
    return task.execute(executor, params)