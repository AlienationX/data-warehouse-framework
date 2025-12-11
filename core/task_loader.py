import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, Optional


class TaskLoader:
    """动态任务加载器"""

    def __init__(self, task_base_dir: Path):
        self.task_base_dir = task_base_dir
        self.tasks: Dict[str, Any] = {}

    def discover_tasks(self, category: Optional[str] = None) -> Dict[str, Any]:
        """发现指定类别的所有任务

        Args:
            category: 任务类别 ('warehouse', 'utils', None表示全部)

        Returns:
            任务字典 {task_name: {module, object, path, category}}
        """
        tasks = {}

        # 确定扫描的目录
        if category == "warehouse":
            scan_dirs = [
                self.task_base_dir / "ods",
                self.task_base_dir / "dw",
                self.task_base_dir / "dim",
            ]
        elif category == "utils":
            scan_dirs = [Path("utils")]
        else:
            scan_dirs = [
                self.task_base_dir / "ods",
                self.task_base_dir / "dw",
                self.task_base_dir / "dim",
                Path("utils"),
            ]

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue

            for py_file in scan_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                task_name = py_file.stem
                module_name = f"{scan_dir.name}.{task_name}"

                try:
                    # 动态导入模块
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 检查模块是否有合适的任务类或函数
                    task_obj = self._extract_task_from_module(module, task_name)
                    if task_obj:
                        cat = "warehouse" if scan_dir.name in ["ods", "dw", "dim"] else "utils"
                        tasks[task_name] = {
                            "module": module,
                            "object": task_obj,
                            "path": py_file,
                            "category": cat,
                        }
                        print("*" * 20, "task_loader", "task", tasks)

                except Exception:
                    pass

        return tasks

    def _extract_task_from_module(self, module, task_name: str) -> Optional[Any]:
        """从模块中提取任务对象"""
        # 优先查找类
        for name, obj in inspect.getmembers(module, inspect.isclass):
            print("=" * 20, "inspect", "name", name, "obj", obj, "task_name", task_name)
            if name.lower().endswith("task"):
                return obj

        # 查找函数
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_") and name != "main":
                return obj

        # 查找main函数
        if hasattr(module, "main") and inspect.isfunction(module.main):
            return module.main

        return None
