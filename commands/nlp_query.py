import typer
from rich import print
from rich.panel import Panel
from rich.box import SIMPLE
from rich.table import Table
from rich.console import Console
import sqlparse
import psycopg2
from psycopg2 import Error
from openai import OpenAI
from typing import Optional
import json
import os

def read_schema_sql() -> str:
    """从schema.sql文件中读取数据库结构"""
    try:
        # 获取当前文件所在目录的上级目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(current_dir, 'schema.sql')
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"无法读取schema.sql: {str(e)}"

def get_sql_from_text(question: str) -> str:
    """使用通义千问将自然语言转换为SQL查询"""
    try:
        client = OpenAI(
            api_key="sk-6d39a5e677c346c5806bea72b523a6cb",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 读取数据库结构
        schema = read_schema_sql()
        
        prompt = f"""作为SQL专家，请根据以下数据库结构和自然语言描述生成PostgreSQL查询语句：

数据库结构：
{schema}

问题描述: {question}

请：
1. 只返回一个完整的SQL查询语句
2. 不要包含任何解释或说明
3. 确保SQL语法正确
4. 使用标准的PostgreSQL语法
5. 只使用schema.sql中定义的表和列名"""

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': '你是一个SQL专家，专门将自然语言转换为精确的SQL查询语句。'},
                {'role': 'user', 'content': prompt}
            ]
        )
        
        response = json.loads(completion.model_dump_json())
        return response['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        return f"转换失败: {str(e)}\n请检查API密钥设置或网络连接。"

def format_results(results, column_names):
    """格式化查询结果"""
    # 预处理日期时间对象，转换为字符串格式
    formatted_results = []
    for row in results:
        formatted_row = []
        for value in row:
            if hasattr(value, 'strftime'):  # 如果是日期时间对象
                formatted_row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                formatted_row.append(str(value) if value is not None else '')
        formatted_results.append(formatted_row)
    return formatted_results

def natural_query(
    question: str = typer.Argument(..., help="用自然语言描述你的查询需求"),
    host: str = typer.Option("localhost", help="数据库主机地址"),
    port: str = typer.Option("5432", help="数据库端口"),
    user: str = typer.Option('postgres', prompt=True, help="数据库用户名"),
    password: str = typer.Option("LZClzc0712!", prompt=True, hide_input=True, help="数据库密码"),
    database: str = "project2025",
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息")
):
    """使用自然语言查询数据库"""
    try:
        # 将自然语言转换为SQL
        sql_query = get_sql_from_text(question)
        
        if sql_query.startswith("转换失败"):
            print(f"[red]{sql_query}[/red]")
            return
        
        # 连接数据库并执行查询
        with psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        ) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql_query)
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    
                    if verbose:
                        # 显示SQL查询
                        formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                        print(Panel(formatted_sql, title="生成的SQL查询"))

                    # 创建表格
                    console = Console()
                    table = Table(show_header=True, header_style="bold", box=SIMPLE, title="查询结果")
                    
                    # 添加列
                    for col in column_names:
                        table.add_column(col)
                    
                    # 添加数据行
                    formatted_results = format_results(results, column_names)
                    for row in formatted_results:
                        table.add_row(*row)
                    
                    # 输出表格
                    console.print("\n")  # 添加一个空行
                    console.print(table)
                    console.print("\n")  # 添加一个空行
                        
                except Error as e:
                    print(f"[red]查询执行错误: {str(e)}[/red]")
                    
    except Error as e:
        print(f"[red]数据库连接错误: {str(e)}[/red]")

if __name__ == "__main__":
    typer.run(natural_query)