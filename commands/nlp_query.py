# nlp_query.py
import json
from commands.schema_info import get_schema_from_db
import psycopg2
import sqlparse
from openai import OpenAI
from psycopg2 import Error
from rich import print
from rich.box import SIMPLE
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_sql_from_text(question: str, config: dict) -> str:
    """使用通义千问将自然语言转换为SQL查询"""
    try:
        client = OpenAI(
            api_key="sk-6d39a5e677c346c5806bea72b523a6cb",  # 可放 config
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # 读取数据库结构
        schema = get_schema_from_db(config, styled=False)

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

        # 显示等待提示动画
        with console.status("[bright_cyan]正在等待大模型生成 SQL，请稍候...[/bright_cyan]", spinner="dots"):
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
        return f"转换失败: {str(e)}"


def run_nlp_query(question: str, db_config: dict):
    """适用于交互模式的自然语言查询"""
    sql_query = get_sql_from_text(question, db_config)

    if sql_query.startswith("转换失败"):
        print(f"[red]{sql_query}[/red]")
        return

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # 格式化SQL
        formatted_sql = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
        print(Panel(formatted_sql, title="生成的SQL查询"))

        # 打印表格
        console = Console()
        table = Table(show_header=True, header_style="bold", box=SIMPLE, title="查询结果")
        for col in column_names:
            table.add_column(col)
        for row in results:
            row_fmt = [str(v) if v is not None else '' for v in row]
            table.add_row(*row_fmt)
        console.print("\n")
        console.print(table)
        console.print("\n")

    except Error as e:
        print(f"[red]查询执行错误: {str(e)}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
