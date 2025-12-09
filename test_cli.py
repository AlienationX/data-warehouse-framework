#!/usr/bin/env python3
"""功能测试脚本"""

import subprocess


def run_cmd(cmd: str) -> tuple[int, str]:
    """运行命令并返回退出码和输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def test_options():
    """测试所有 Options"""
    tests = [
        ("主帮助信息", "python main.py --help"),
        ("版本信息 (--version)", "python main.py --version"),
        ("版本信息 (-V)", "python main.py -V"),
        ("带日期的帮助", "python main.py --start-date 2025-01-01 --end-date 2025-12-31 --help"),
        ("详细模式", "python main.py -v list-tasks"),
        ("执行器选项", "python main.py --executor mysql list-tasks"),
    ]

    print("=" * 60)
    print("📋 测试 Options 功能")
    print("=" * 60)

    for name, cmd in tests:
        code, output = run_cmd(cmd)
        status = "✅" if code == 0 else "❌"
        print(f"{status} {name}")
        if code != 0:
            print(f"   Error: {output[:100]}")


def test_commands():
    """测试所有 Commands"""
    tests = [
        ("list-tasks", "python main.py list-tasks"),
        ("warehouse 列表", "python main.py warehouse"),
        ("utils 列表", "python main.py utils"),
        ("version", "python main.py version"),
    ]

    print("\n" + "=" * 60)
    print("🎯 测试 Commands 功能")
    print("=" * 60)

    for name, cmd in tests:
        code, output = run_cmd(cmd)
        status = "✅" if code == 0 else "❌"
        print(f"{status} {name}")
        if code != 0:
            print(f"   Error: {output[:100]}")
        else:
            # 显示输出摘要
            lines = output.strip().split("\n")
            for line in lines[:3]:
                print(f"   {line}")


def test_warehouse_tasks():
    """测试 warehouse 分类下的任务"""
    print("\n" + "=" * 60)
    print("📦 测试 Warehouse 任务")
    print("=" * 60)

    # 先获取可用任务
    code, output = run_cmd("python main.py warehouse")
    if "ods_yb_master_info" in output:
        print("✅ ods_yb_master_info 任务已发现")
    else:
        print("❌ ods_yb_master_info 任务未发现")

    if "dim_date" in output:
        print("✅ dim_date 任务已发现")
    else:
        print("❌ dim_date 任务未发现")


def test_utils_tasks():
    """测试 utils 分类下的任务"""
    print("\n" + "=" * 60)
    print("🛠️  测试 Utils 任务")
    print("=" * 60)

    # 先获取可用任务
    code, output = run_cmd("python main.py utils")
    tasks = ["to_csv", "to_excel", "print_schema", "print_depends"]

    for task in tasks:
        if task in output:
            print(f"✅ {task} 任务已发现")
        else:
            print(f"❌ {task} 任务未发现")


def main():
    """主测试函数"""
    print("\n🚀 开始功能测试...\n")

    test_options()
    test_commands()
    test_warehouse_tasks()
    test_utils_tasks()

    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n使用示例:")
    print("  python main.py --help                    # 显示帮助")
    print("  python main.py --version                 # 显示版本")
    print("  python main.py -v warehouse              # 详细模式列出 warehouse 任务")
    print("  python main.py warehouse ods_yb_master_info  # 执行指定任务")
    print("  python main.py utils to_csv              # 执行指定 utils 任务")
    print("  python main.py list-tasks -d             # 列出所有任务（详细模式）")


if __name__ == "__main__":
    main()
