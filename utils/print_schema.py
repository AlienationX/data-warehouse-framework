"""打印数据库表结构"""


def print_schema(executor, params):
    """打印数据库表结构

    参数:
        executor: 数据库执行器
        params: 参数字典，包含 table_name 等
    """
    table_name = params.get("table_name", "information_schema.tables")

    try:
        # 获取表结构信息
        sql = f"DESCRIBE {table_name}" if hasattr(executor, "database_type") else f"DESC {table_name}"
        result = executor.execute_query(sql)

        if result:
            print(f"表 {table_name} 的结构:")
            print("-" * 80)
            for row in result:
                print(row)
            print("-" * 80)
            return {"status": "success", "rows": len(result)}
        else:
            print(f"⚠️ 未找到表: {table_name}")
            return {"status": "not_found"}

    except Exception as e:
        print(f"❌ 获取表结构失败: {e}")
        return {"status": "failed", "error": str(e)}
