import typer
from rich import print
import psycopg2
from psycopg2 import Error

def reset_db(
    host: str = typer.Option("localhost", help="数据库主机地址"),
    port: str = typer.Option("5432", help="数据库端口"),
    user: str = typer.Option(..., prompt=True, help="数据库用户名"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="数据库密码"),
    database: str = "project2025"
):
    """重置数据库系统"""
    try:
        # 连接到默认数据库
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 断开所有连接
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND pid <> pg_backend_pid();
        """)
        
        # 删除并重新创建数据库
        cursor.execute(f"DROP DATABASE IF EXISTS {database}")
        cursor.execute(f"CREATE DATABASE {database}")
        print(f"[green]已重置数据库 {database}[/green]")
        
    except Error as e:
        print(f"[red]重置系统失败: {str(e)}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")

if __name__ == "__main__":
    typer.run(reset_db)