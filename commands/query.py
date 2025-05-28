# query.py
import psycopg2
from psycopg2 import Error
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from commands.config import load_config
from commands.validate import get_ai_analysis

console = Console()
# 加载持久化的数据库配置
db_config = load_config()

def run_query(sql: str):
    try:
        print("[blue]正在连接数据库...[/blue]")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        print(f"[blue]正在执行查询: {sql}[/blue]")
        cursor.execute(sql)

        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
        else:
            print("[yellow]查询执行成功，但没有返回结果。[/yellow]")
            return

        # 打印查询结果
        table = Table(title="查询结果")
        for column in column_names:
            table.add_column(column)
        for row in results:
            table.add_row(*[str(value) if value is not None else '' for value in row])
        print(table)

    except Error as e:
        error_msg = str(e)
        print(f"[red]查询执行失败: {error_msg}[/red]")

        # ⛔ 判断是否为语法类错误
        syntax_keywords = [
            "syntax error", "does not exist", "relation", "missing", "invalid input",
            "column", "table", "permission denied", "unterminated", "unexpected"
        ]

        if any(kw in error_msg.lower() for kw in syntax_keywords):
            try:
                with console.status("[cyan]正在分析 SQL 错误，请稍候...[/cyan]", spinner="dots"):
                    ai_result = get_ai_analysis(sql, error_msg)

                print(Panel(ai_result, title="AI 错误分析与建议", subtitle="由通义千问提供"))
            except Exception as ai_err:
                print(f"[yellow]AI 分析失败：{ai_err}[/yellow]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")
