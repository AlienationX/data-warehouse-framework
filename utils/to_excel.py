"""导出数据到 Excel 文件"""


def export_to_excel(executor, params):
    """将数据库查询结果导出到 Excel 文件

    参数:
        executor: 数据库执行器
        params: 参数字典，包含 sql, output_path 等
    """
    sql = params.get("sql", "SELECT 1")
    output_path = params.get("output_path", "output.xlsx")

    try:
        # 执行查询
        result = executor.execute_query(sql)

        # 导出到 Excel
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active

        if result:
            if isinstance(result, list) and len(result) > 0:
                for row in result:
                    ws.append(row)
                wb.save(output_path)
                print(f"✅ 数据已导出到: {output_path}")

        return {"status": "success", "output": output_path}
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return {"status": "failed", "error": str(e)}
