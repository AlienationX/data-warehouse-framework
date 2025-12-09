from typing import Dict, Any, Optional
import re

class SQLBuilder:
    """SQL构建器，支持参数化SQL拼接"""
    
    @staticmethod
    def build_sql(template: str, params: Dict[str, Any]) -> str:
        """根据模板和参数构建SQL"""
        sql = template
        
        # 替换参数占位符
        for key, value in params.items():
            placeholder = f"${{{key}}}"
            if placeholder in sql:
                if isinstance(value, str):
                    # 字符串值需要转义
                    value = value.replace("'", "''")
                    sql = sql.replace(placeholder, f"'{value}'")
                else:
                    sql = sql.replace(placeholder, str(value))
        
        # 处理条件逻辑
        sql = SQLBuilder._process_conditional_logic(sql, params)
        
        return sql
    
    @staticmethod
    def _process_conditional_logic(sql: str, params: Dict[str, Any]) -> str:
        """处理条件逻辑（如IF-ELSE）"""
        # 简单的条件逻辑处理，例如：/* IF condition */ ... /* ENDIF */
        lines = sql.split('\n')
        result_lines = []
        skip_mode = False
        condition_stack = []
        
        for line in lines:
            if '/* IF' in line:
                # 提取条件
                match = re.search(r'/\*\s*IF\s+(\w+)\s*\*/', line)
                if match:
                    condition = match.group(1)
                    should_include = params.get(condition, False)
                    condition_stack.append(should_include)
                    if not should_include:
                        skip_mode = True
                    result_lines.append(line.replace(match.group(0), '').strip())
                else:
                    result_lines.append(line)
            elif '/* ENDIF */' in line:
                if condition_stack:
                    condition_stack.pop()
                    skip_mode = any(not cond for cond in condition_stack)
                result_lines.append(line.replace('/* ENDIF */', '').strip())
            elif not skip_mode:
                result_lines.append(line)
        
        return '\n'.join([line for line in result_lines if line])