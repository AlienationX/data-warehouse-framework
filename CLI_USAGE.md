# 数据仓库框架 CLI 使用文档

## 功能概述

该 CLI 框架支持以下功能：

### Options（全局选项）

| 选项 | 短形式 | 说明 | 默认值 |
|------|--------|------|--------|
| `--version` | `-V` | 显示版本信息 | - |
| `--start-date` | - | 开始日期 (YYYY-MM-DD) | None |
| `--end-date` | - | 结束日期 (YYYY-MM-DD) | None |
| `--executor` | - | 执行器类型 (hive/mysql/postgresql) | hive |
| `--verbose` | `-v` | 详细输出模式 | False |
| `--dry-run` | - | 干跑模式，只生成SQL不执行 | False |
| `--config-file` | - | 配置文件路径 | None |
| `--help` | `-h` | 显示帮助信息 | - |

### Commands（主命令）

#### 1. `warehouse` - 数仓任务管理
```bash
# 列出 warehouse 类别的所有任务
python main.py warehouse

# 执行指定的 warehouse 任务
python main.py warehouse <task_name>
```

**支持的任务：**
- `ods_yb_master_info` - ODS 原始数据
- `dim_date` - 维度表日期
- (其他 ods/dw/dim 目录下的任务)

#### 2. `utils` - 工具函数
```bash
# 列出 utils 分类的所有工具任务
python main.py utils

# 执行指定的工具任务
python main.py utils <task_name>
```

**支持的任务：**
- `to_csv` - 导出数据到 CSV
- `to_excel` - 导出数据到 Excel
- `print_schema` - 打印表结构
- `print_depends` - 打印任务依赖

#### 3. `list-tasks` - 列出所有任务
```bash
# 简略显示
python main.py list-tasks

# 详细显示（包含文件路径）
python main.py list-tasks -d
python main.py list-tasks --detail
```

#### 4. `run-all` - 批量执行任务
```bash
# 执行所有任务，结果保存到 results 目录
python main.py run-all

# 过滤执行特定前缀的任务
python main.py run-all -f ods

# 指定输出目录
python main.py run-all -d /path/to/output
```

#### 5. `version` - 查看版本
```bash
python main.py version
```

## 使用示例

### 基础用法

```bash
# 显示帮助
python main.py --help

# 显示版本
python main.py --version
python main.py -V

# 列出所有任务
python main.py list-tasks
python main.py list-tasks --detail
```

### Warehouse 任务

```bash
# 列出所有 warehouse 任务
python main.py warehouse

# 执行特定任务
python main.py warehouse ods_yb_master_info

# 带详细输出
python main.py -v warehouse ods_yb_master_info

# 指定执行器和日期范围
python main.py --executor mysql --start-date 2025-01-01 --end-date 2025-12-31 warehouse dim_date
```

### Utils 任务

```bash
# 列出所有工具任务
python main.py utils

# 执行 CSV 导出
python main.py utils to_csv sql="SELECT * FROM table" output_path="output.csv"

# 执行 Excel 导出
python main.py utils to_excel sql="SELECT * FROM table" output_path="output.xlsx"

# 打印表结构
python main.py utils print_schema table_name="users"

# 打印任务依赖
python main.py utils print_depends task_name="ods_yb_master_info"
```

### 高级用法

```bash
# 干跑模式（只生成SQL，不执行）
python main.py --dry-run warehouse ods_yb_master_info

# 详细模式 + MySQL 执行器
python main.py -v --executor mysql warehouse dim_date

# 批量执行并输出结果
python main.py run-all --filter ods --output-dir ./my_results

# 组合全局选项
python main.py \
  --executor postgresql \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  -v \
  warehouse ods_yb_master_info
```

## 参数传递

任务参数使用 `key=value` 格式传递：

```bash
# 单个参数
python main.py warehouse ods_yb_master_info table_name=users

# 多个参数
python main.py utils to_csv \
  sql="SELECT * FROM users" \
  output_path="users.csv" \
  encoding="utf-8"
```

## 输出文件

使用 `-o` 或 `--output` 选项保存任务结果到文件：

```bash
# 保存为 JSON
python main.py warehouse ods_yb_master_info -o result.json
python main.py warehouse ods_yb_master_info --output result.json
```

## 配置文件

使用 `--config-file` 指定配置文件：

```bash
python main.py --config-file /path/to/config.yaml warehouse ods_yb_master_info
```

## 项目结构

```
warehouse/
  ├── ods/              # 原始数据层任务
  ├── dw/               # 数据仓库层任务
  ├── dim/              # 维度表任务
  └── base_task.py      # 任务基类

utils/
  ├── to_csv.py         # CSV 导出工具
  ├── to_excel.py       # Excel 导出工具
  ├── print_schema.py   # 表结构打印工具
  └── print_depends.py  # 任务依赖分析工具
```

## 开发指南

### 添加新任务

1. **Warehouse 任务**：在 `warehouse/ods/`、`warehouse/dw/` 或 `warehouse/dim/` 目录下创建 `.py` 文件

```python
# warehouse/ods/my_task.py
class MyTask:
    def __init__(self):
        self.description = "我的任务描述"
    
    def get_sql_template(self) -> str:
        return "SELECT * FROM table WHERE date >= :start_date"
    
    def execute(self, executor, params):
        # 实现任务逻辑
        pass
```

2. **Utils 任务**：在 `utils/` 目录下创建 `.py` 文件

```python
# utils/my_tool.py
def my_tool(executor, params):
    """我的工具函数"""
    # 实现工具逻辑
    return {"status": "success"}
```

### 任务命名规则

- 类式任务：类名必须以 `Task` 结尾（如 `MyTask`）
- 函数式任务：函数不能以 `_` 开头，且不能是 `main`
- 文件名转换为任务名，例如 `ods_yb_master_info.py` → 任务名 `ods_yb_master_info`

## 常见问题

### Q: 如何在任务中使用日期参数？
A: 通过全局选项 `--start-date` 和 `--end-date`，这些会自动传递到任务的 `params` 参数中。

### Q: 如何指定不同的数据库执行器？
A: 使用 `--executor` 选项，支持 `hive`、`mysql`、`postgresql`。

### Q: 如何查看任务的详细信息？
A: 使用 `-v` 或 `--verbose` 选项启用详细输出模式。

### Q: 如何在没有执行的情况下测试 SQL？
A: 使用 `--dry-run` 选项。

## 更新日志

### v1.0.0 (2025-12-09)
- ✅ 完成 Options 功能（--start-date, --end-date, --executor, -v, -V, --version, --help）
- ✅ 完成 Commands 功能（warehouse, utils）
- ✅ 支持 warehouse 下的 ods/dw/dim 目录任务
- ✅ 支持 utils 目录下的工具函数
- ✅ 实现参数化任务执行
- ✅ 支持结果输出到文件
