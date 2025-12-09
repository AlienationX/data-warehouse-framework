import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from config import config
from core.task_loader import TaskLoader
from executor.base_executor import ExecutorFactory

APP_NAME = "Awesome CLI 数据仓库任务调度器"
APP_VERSION = "1.0.0"

app = typer.Typer(
    name=APP_NAME,
    help="基于Typer的数据仓库任务执行系统",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode=None,
)

# 全局任务加载器
task_loader = TaskLoader(Path("warehouse"))


def get_common_params(
    executor_type: str = typer.Option("hive", "--executor", help="执行器类型: hive/mysql/postgresql"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="结束日期 (YYYY-MM-DD)"),
    dry_run: bool = typer.Option(False, help="干跑模式，只生成SQL不执行"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="详细输出"),
    config_file: Path = typer.Option(None, help="配置文件路径"),
) -> Dict[str, Any]:
    """获取通用参数"""
    common_params = {
        "executor_type": executor_type,
        "start_date": start_date,
        "end_date": end_date,
        "dry_run": dry_run,
        "verbose": verbose,
        "run_time": datetime.now().isoformat(),
    }

    if config_file:
        config.load_from_file(config_file)

    return common_params


@app.callback(invoke_without_command=True)
def version_callback(
    ctx: typer.Context,
    version: bool = typer.Option(None, "-V", "--version", help="显示版本信息"),
    executor_type: str = typer.Option("hive", "--executor", help="执行器类型"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="开始日期"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="结束日期"),
    dry_run: bool = typer.Option(False, help="干跑模式"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="详细输出"),
    config_file: Path = typer.Option(None, help="配置文件"),
):
    """主回调函数"""
    # 处理版本信息
    if version:
        typer.echo(f"{APP_NAME} v{APP_VERSION}")
        raise typer.Exit()

    # 存储上下文对象
    ctx.obj = get_common_params(executor_type, start_date, end_date, dry_run, verbose, config_file)


def create_task_command(task_name: str, task_info: Dict[str, Any]):
    """动态创建任务命令"""

    @app.command(name=task_name)
    def task_command(
        ctx: typer.Context,
        task_params: List[str] = typer.Argument(None, help="任务参数，格式: key=value"),
        output_file: Optional[Path] = typer.Option(None, "-o", "--output", help="结果输出文件"),
    ):
        """动态生成的任务命令"""
        # 解析任务参数
        params_dict = {}
        if task_params:
            for param in task_params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    params_dict[key.strip()] = value.strip()

        # 合并参数
        all_params = {**ctx.obj, **params_dict}

        # 执行任务
        execute_single_task(task_name, task_info, all_params, output_file)

    # 更新命令文档
    task_obj = task_info["object"]
    if hasattr(task_obj, "description"):
        task_command.__doc__ = task_obj.description

    return task_command


def execute_single_task(task_name: str, task_info: Dict[str, Any], params: Dict[str, Any], output_file: Optional[Path] = None):
    """执行单个任务"""
    try:
        if params.get("verbose"):
            typer.echo(f"🚀 开始执行任务: {task_name}")
            typer.echo(f"   参数: {params}")

        # 创建执行器
        executor_type = params["executor_type"]
        executor_config = config.executors.get(executor_type, {}).get("config", {})

        with ExecutorFactory.create_executor(executor_type, executor_config) as executor:
            # 执行任务
            task_obj = task_info["object"]

            if callable(task_obj):
                # 函数式任务
                result = task_obj(executor, params)
            else:
                # 类式任务
                if isinstance(task_obj, type):
                    # 是类，需要实例化
                    task_instance = task_obj()
                    if hasattr(task_instance, "validate_params"):
                        task_instance.validate_params(params)
                    result = task_instance.execute(executor, params)
                else:
                    # 已经是实例
                    result = task_obj.execute(executor, params)

            # 处理结果
            if output_file:
                with open(output_file, "w") as f:
                    if isinstance(result, (dict, list)):
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    else:
                        f.write(str(result))
                typer.echo(f"💾 结果已保存到: {output_file}")

            typer.echo(f"✅ 任务 {task_name} 执行完成")
            return result

    except Exception as e:
        typer.echo(f"❌ 任务执行失败: {e}", err=True)
        if params.get("verbose"):
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def list_tasks(ctx: typer.Context, detail: bool = typer.Option(False, "-d", "--detail", help="显示详细信息")):
    """列出所有可用任务"""
    tasks = task_loader.discover_tasks()

    if not tasks:
        typer.echo("❌ 未发现任何任务")
        return

    typer.echo(f"📋 发现 {len(tasks)} 个任务:\n")

    # 按类别分组
    warehouse_tasks = {k: v for k, v in tasks.items() if v.get("category") == "warehouse"}
    utils_tasks = {k: v for k, v in tasks.items() if v.get("category") == "utils"}

    if warehouse_tasks:
        typer.echo("📦 Warehouse 任务:")
        for i, (task_name, task_info) in enumerate(warehouse_tasks.items(), 1):
            if detail:
                typer.echo(f"   {i}. {task_name} - {task_info['path']}")
            else:
                typer.echo(f"   {i}. {task_name}")

    if utils_tasks:
        typer.echo("\n🛠️  Utils 任务:")
        for i, (task_name, task_info) in enumerate(utils_tasks.items(), 1):
            if detail:
                typer.echo(f"   {i}. {task_name} - {task_info['path']}")
            else:
                typer.echo(f"   {i}. {task_name}")


@app.command()
def run_all(
    ctx: typer.Context,
    task_filter: Optional[str] = typer.Option(None, "-f", "--filter", help="任务名称过滤"),
    output_dir: Path = typer.Option("results", "-d", "--output-dir", help="输出目录"),
):
    """批量执行所有任务"""
    tasks = task_loader.discover_tasks()

    if not tasks:
        typer.echo("❌ 没有可执行的任务")
        return

    # 过滤任务
    if task_filter:
        filtered_tasks = {k: v for k, v in tasks.items() if task_filter in k}
    else:
        filtered_tasks = tasks

    if not filtered_tasks:
        typer.echo(f"❌ 没有匹配的任务: {task_filter}")
        return

    output_dir.mkdir(exist_ok=True)

    with typer.progressbar(filtered_tasks.items(), label="执行任务") as progress:
        for task_name, task_info in progress:
            try:
                output_file = output_dir / f"{task_name}_result.json"
                execute_single_task(task_name, task_info, ctx.obj, output_file)
            except Exception as e:
                typer.echo(f"⚠️ 任务 {task_name} 执行失败: {e}")


def create_category_command(category: str):
    """为指定类别创建子命令组"""

    @app.command()
    def category_command(
        ctx: typer.Context,
    ):
        """分类命令组"""
        # 获取该类别的所有任务
        tasks = task_loader.discover_tasks(category=category)

        if not tasks:
            typer.echo(f"❌ {category} 类别中没有任务")
            return

        # 动态注册任务子命令
        for task_name, task_info in tasks.items():
            if task_name not in [cmd.name for cmd in app.registered_commands]:
                create_task_command(task_name, task_info)

        typer.echo(f"✅ {category} 类别已加载 {len(tasks)} 个任务")

    category_command.__doc__ = f"{category.upper()} 任务分类"
    return category_command


@app.command()
def warehouse(
    ctx: typer.Context,
    task: Optional[str] = typer.Argument(None, help="具体任务名称"),
):
    """Warehouse 数仓任务 (ods/dw/dim)"""
    tasks = task_loader.discover_tasks(category="warehouse")

    if not tasks:
        typer.echo("❌ Warehouse 类别中没有任务")
        return

    if task is None:
        # 列出该类别的所有任务
        typer.echo(f"📦 Warehouse 可用任务 ({len(tasks)} 个):")
        for i, task_name in enumerate(tasks.keys(), 1):
            typer.echo(f"   {i}. {task_name}")
        typer.echo("\n使用: python main.py warehouse <task_name>")
        return

    if task in tasks:
        # 执行指定任务
        task_info = tasks[task]
        execute_single_task(task, task_info, ctx.obj)
    else:
        typer.echo(f"❌ 未找到任务: {task}")
        typer.echo(f"可用任务: {', '.join(tasks.keys())}")
        raise typer.Exit(code=1)


@app.command()
def utils(
    ctx: typer.Context,
    task: Optional[str] = typer.Argument(None, help="具体任务名称"),
):
    """Utils 工具函数"""
    tasks = task_loader.discover_tasks(category="utils")

    if not tasks:
        typer.echo("❌ Utils 类别中没有任务")
        return

    if task is None:
        # 列出该类别的所有任务
        typer.echo(f"🛠️  Utils 可用任务 ({len(tasks)} 个):")
        for i, task_name in enumerate(tasks.keys(), 1):
            typer.echo(f"   {i}. {task_name}")
        typer.echo("\n使用: python main.py utils <task_name>")
        return

    if task in tasks:
        # 执行指定任务
        task_info = tasks[task]
        execute_single_task(task, task_info, ctx.obj)
    else:
        typer.echo(f"❌ 未找到任务: {task}")
        typer.echo(f"可用任务: {', '.join(tasks.keys())}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """查看版本信息"""
    typer.echo(f"{APP_NAME} v{APP_VERSION}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
    else:
        typer.echo(f"🚀 执行子命令: {ctx.invoked_subcommand}")


if __name__ == "__main__":
    app()
