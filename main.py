import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click
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
    rich_markup_mode="rich",
)


# 创建两个子应用（group），在 help 中加入简短描述与示例
warehouse_app = typer.Typer(
    help=(
        "Warehouse 分类任务（对应 warehouse/ods | dw | dim 下的 .py 文件）。\n\n"
        "Examples:\n"
        "  python main.py warehouse ods_yb_master_info --executor mysql --dry-run --verbose\n\n"
        "列出命令：\n"
        "  python main.py warehouse --help"
    )
)

utils_app = typer.Typer(
    help=(
        "Utils 分类工具（对应 utils/ 下的 .py 文件）。\n\n"
        "Examples:\n"
        "  main.py utils to_csv -o out.csv --verbose\n\n"
        "列出命令：\n  main.py utils --help"
    )
)

# 注册到主应用
app.add_typer(warehouse_app, name="warehouse")
app.add_typer(utils_app, name="utils")


# 任务加载器（指向 warehouse 根目录）
task_loader = TaskLoader(Path("warehouse"))


def execute_single_task(task_name: str, task_info: Dict[str, Any], params: Dict[str, Any], output_file: Optional[Path] = None):
    """执行单个任务（通用实现）"""
    try:
        if params.get("verbose"):
            typer.echo(f"🚀 开始执行任务: {task_name}")
            typer.echo(f"   参数: {params}")

        executor_type = params.get("executor", "hive")
        executor_config = config.executors.get(executor_type, {}).get("config", {})

        with ExecutorFactory.create_executor(executor_type, executor_config) as executor:
            task_obj = task_info["object"]
            print("*" * 20, "task_obj", task_obj)

            if isinstance(task_obj, type):
                task_instance = task_obj()
                if hasattr(task_instance, "validate_params"):
                    task_instance.validate_params(params)
                result = task_instance.execute(executor, params)
            elif callable(task_obj):
                result = task_obj(executor, params)
            else:
                result = task_obj.execute(executor, params)

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


# 动态注册 warehouse 下的所有任务作为命令
warehouse_tasks = task_loader.discover_tasks(category="warehouse")
print("*" * 20, "warehouse_tasks", warehouse_tasks)
for task_name in sorted(warehouse_tasks.keys()):
    task_info = warehouse_tasks[task_name]
    print("*" * 20, "task_info", task_info)

    def create_warehouse_command(task_name: str, task_info: Dict[str, Any]):
        """工厂函数创建具体任务命令"""

        def task_command(
            executor: str = typer.Option("hive", "--executor", help="执行器类型: hive/mysql/postgresql"),
            start_date: Optional[str] = typer.Option(None, "--start-date", help="开始日期 (YYYY-MM-DD)"),
            end_date: Optional[str] = typer.Option(None, "--end-date", help="结束日期 (YYYY-MM-DD)"),
            dry_run: bool = typer.Option(False, "--dry-run", help="干跑模式，只生成SQL不执行"),
            verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
        ):
            """执行具体任务"""
            # 合并 group-level 参数（如果 group 提供了非默认值，则作为子命令的默认）
            ctx = click.get_current_context()
            parent_obj = getattr(ctx.parent, "obj", {}) if ctx.parent is not None else {}
            group_params = parent_obj.get("warehouse_group_params", {}) if parent_obj else {}

            defaults = {"executor": "hive", "start_date": None, "end_date": None, "dry_run": False, "verbose": False}
            sub_params = {
                "executor": executor,
                "start_date": start_date,
                "end_date": end_date,
                "dry_run": dry_run,
                "verbose": verbose,
            }

            params = {}
            for k, dv in defaults.items():
                if (
                    k in group_params
                    and group_params.get(k) is not None
                    and sub_params.get(k) == dv
                    and group_params.get(k) != dv
                ):
                    params[k] = group_params.get(k)
                else:
                    params[k] = sub_params.get(k)

            params["run_time"] = datetime.now().isoformat()
            execute_single_task(task_name, task_info, params)

        task_command.__doc__ = f"执行任务: {task_name}"
        task_command.__name__ = task_name
        return task_command

    warehouse_app.command(name=task_name)(create_warehouse_command(task_name, task_info))
    # warehouse_app.command(name=task_name, help="xxxx")(create_warehouse_command(task_name, task_info))


# 动态注册 utils 下的所有工具作为命令
utils_tasks = task_loader.discover_tasks(category="utils")
for tool_name in sorted(utils_tasks.keys()):
    tool_info = utils_tasks[tool_name]

    def create_utils_command(tool_name: str, tool_info: Dict[str, Any]):
        """工厂函数创建具体工具命令"""

        def tool_command(
            output: Optional[Path] = typer.Option(None, "--output", "-o", help="结果输出文件（可选）"),
            verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
        ):
            """执行具体工具"""
            # 合并 group-level 参数（utils）
            ctx = click.get_current_context()
            parent_obj = getattr(ctx.parent, "obj", {}) if ctx.parent is not None else {}
            group_params = parent_obj.get("utils_group_params", {}) if parent_obj else {}

            defaults = {"output": None, "verbose": False}
            sub_params = {"output": str(output) if output else None, "verbose": verbose}

            params = {}
            for k, dv in defaults.items():
                if (
                    k in group_params
                    and group_params.get(k) is not None
                    and sub_params.get(k) == dv
                    and group_params.get(k) != dv
                ):
                    params[k] = group_params.get(k)
                else:
                    params[k] = sub_params.get(k)

            params["run_time"] = datetime.now().isoformat()
            execute_single_task(tool_name, tool_info, params, Path(params["output"]) if params.get("output") else None)

        tool_command.__doc__ = f"执行工具: {tool_name}"
        tool_command.__name__ = tool_name
        return tool_command

    utils_app.command(name=tool_name)(create_utils_command(tool_name, tool_info))
# group-level callbacks（在文件末尾统一定义）


@warehouse_app.callback(invoke_without_command=True)
def warehouse_group_callback(
    ctx: typer.Context,
    executor: str = typer.Option("hive", "--executor", help="执行器类型: hive/mysql/postgresql"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="结束日期 (YYYY-MM-DD)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="干跑模式，只生成SQL不执行"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
):
    ctx.ensure_object(dict)
    ctx.obj["warehouse_group_params"] = {
        "executor": executor,
        "start_date": start_date,
        "end_date": end_date,
        "dry_run": dry_run,
        "verbose": verbose,
    }
    # 如果未指定子命令，输出提示并展示该 group 的帮助
    if ctx.invoked_subcommand is None:
        typer.echo("请使用 --help 查看可用的 warehouse 子命令和选项：\n")
        typer.echo(ctx.get_help())
        raise typer.Exit()


@utils_app.callback(invoke_without_command=True)
def utils_group_callback(
    ctx: typer.Context,
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="结果输出文件（可选）"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
):
    ctx.ensure_object(dict)
    ctx.obj["utils_group_params"] = {"output": str(output) if output else None, "verbose": verbose}
    # 如果未指定子命令，输出提示并展示该 group 的帮助
    if ctx.invoked_subcommand is None:
        typer.echo("请使用 --help 查看可用的 utils 子命令和选项：\n")
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context, version: bool = typer.Option(False, "-v", "--version", help="显示版本信息")):
    """顶层回调：仅处理版本显示或欢迎信息"""
    if version:
        typer.echo(f"{APP_NAME} v{APP_VERSION}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(f"欢迎使用 {APP_NAME} CLI 工具")
        typer.echo("使用 --help 查看命令: warehouse, utils")


if __name__ == "__main__":
    app()
