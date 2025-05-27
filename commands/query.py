# query.py
from rich import print
from rich.table import Table
import psycopg2
from psycopg2 import Error
from commands.config import load_config

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

        table = Table(title="查询结果")
        for column in column_names:
            table.add_column(column)
        for row in results:
            table.add_row(*[str(value) for value in row])
        print(table)

    except Error as e:
        print(f"[red]查询执行失败: {str(e)}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")

