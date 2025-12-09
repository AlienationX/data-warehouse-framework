"""导出数据到 CSV 文件"""


def export_to_csv(executor, params):
    """将数据库查询结果导出到 CSV 文件

    参数:
        executor: 数据库执行器
        params: 参数字典，包含 sql, output_path 等
    """
    sql = params.get("sql", "SELECT 1")
    output_path = params.get("output_path", "output.csv")

    try:
        # 执行查询
        result = executor.execute_query(sql)

        # 导出到 CSV
        import csv

        if result:
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                if isinstance(result, list) and len(result) > 0:
                    # 写入数据
                    writer.writerows(result)
                    print(f"✅ 数据已导出到: {output_path}")
        return {"status": "success", "output": output_path}
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return {"status": "failed", "error": str(e)}
