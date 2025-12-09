from warehouse.base_task import BaseTask


class Task(BaseTask):
    """日期维度表任务"""

    def __init__(self):
        super().__init__()
        self.description = "日期维度表构建任务"

    def get_sql_template(self) -> str:
        return """
        INSERT INTO dim.dim_date
        SELECT 
            date_id,
            date_value,
            year,
            month,
            day,
            quarter,
            is_weekend
        FROM source.date_source
        WHERE date_value BETWEEN '${start_date}' AND '${end_date}'
        """

    def validate_params(self, params) -> bool:
        required_params = ["start_date", "end_date"]
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必要参数: {param}")
        return True
