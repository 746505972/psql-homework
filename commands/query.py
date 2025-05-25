import typer
from rich import print
from rich.table import Table
import psycopg2
from psycopg2 import Error

def execute_query(
    query: str = typer.Argument(..., help="要执行的SQL查询语句"),
    host: str = typer.Option("localhost", help="数据库主机地址"),
    port: str = typer.Option("5432", help="数据库端口"),
    user: str = typer.Option('postgres', prompt=True, help="数据库用户名"),
    password: str = typer.Option('LZClzc0712!', prompt=True, hide_input=True, help="数据库密码"),
    database: str = "project2025"
):
    """执行SQL查询并显示结果"""
    try:
        print("[blue]正在连接数据库...[/blue]")
        # 连接数据库
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # 执行查询
        print(f"[blue]正在执行查询: {query}[/blue]")
        cursor.execute(query)
        
        # 获取列名（仅对SELECT查询有效）
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
        else:
            print("[yellow]查询执行成功，但没有返回结果。[/yellow]")
            return
        
        # 创建表格
        table = Table(title="查询结果")
        
        # 添加列
        for column in column_names:
            table.add_column(column)
            
        # 添加数据行
        for row in results:
            table.add_row(*[str(value) for value in row])
            
        # 显示结果
        print(table)
        
    except Error as e:
        print(f"[red]查询执行失败: {str(e)}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")

if __name__ == "__main__":
    typer.run(execute_query)