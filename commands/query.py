# query.py
import psycopg2
from psycopg2 import Error
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from commands.validate import get_ai_analysis

console = Console()


def run_query(sql: str, db_config: dict):
    try:
        print("[blue]正在连接数据库...[/blue]")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        print(f"[blue]正在执行查询: {sql}[/blue]")
        cursor.execute(sql)

        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            # 打印查询结果
            table = Table(title="查询结果", show_lines=True)

            table.add_column("")  # 添加无标题的索引列
            for column in column_names:
                table.add_column(f"[bold bright_cyan]{column}[/bold bright_cyan]", style="white")

            for idx, row in enumerate(results, start=1):
                row_data = [str(value) if value is not None else '' for value in row]
                table.add_row(str(idx), *row_data)  # 将索引作为首列
            console.print(table)


        else:
            print("[yellow]查询执行成功，但没有返回结果。[/yellow]")

        # 添加 EXPLAIN ANALYZE 分析
        try:
            explain_sql = f"EXPLAIN ANALYZE {sql}"
            cursor.execute(explain_sql)
            plan = cursor.fetchall()
            explain_text = "\n".join([row[0] for row in plan])

            console.print(Panel(explain_text, title="EXPLAIN ANALYZE"))

        except Exception as explain_err:
            print(f"[yellow]EXPLAIN ANALYZE 执行失败: {explain_err}[/yellow]")

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
