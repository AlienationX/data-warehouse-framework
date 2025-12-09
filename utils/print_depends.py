"""打印任务依赖关系"""


def print_depends(executor, params):
    """打印任务的依赖关系

    参数:
        executor: 数据库执行器
        params: 参数字典，包含 task_name 等
    """
    from core.task_depends import TaskDepends

    task_name = params.get("task_name")

    try:
        depends_analyzer = TaskDepends()
        deps = depends_analyzer.analyze(task_name)

        if deps:
            print(f"任务 {task_name} 的依赖关系:")
            print("-" * 50)
            for dep in deps:
                print(f"  ➜ {dep}")
            print("-" * 50)
            return {"status": "success", "dependencies": deps}
        else:
            print(f"任务 {task_name} 无依赖")
            return {"status": "success", "dependencies": []}

    except Exception as e:
        print(f"❌ 分析依赖失败: {e}")
        return {"status": "failed", "error": str(e)}
