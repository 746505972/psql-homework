import typer
from rich import print
from rich.table import Table
import psycopg2
from psycopg2 import Error

def init_db(
    host: str = typer.Option("localhost", help="数据库主机地址"),
    port: str = typer.Option("5432", help="数据库端口"),
    user: str = typer.Option(..., prompt=True, help="用户名"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="密码"),
    db_name: str = "project2025"
):
    """检查数据库结构和数据"""
    try:
        print(f"[blue]正在连接到数据库 {db_name}...[/blue]")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()

        # 获取所有表名
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()

        print("\n[green]数据库中的表:[/green]")
        for table in tables:
            table_name = table[0]
            # 获取每个表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = cursor.fetchone()
            count = result[0] if result is not None else 0
            print(f"[blue]- {table_name}: {count} 条记录[/blue]")

        print("\n[green]数据库初始化验证完成！[/green]")
        return True

    except Error as e:
        print(f"[red]数据库连接失败: {str(e)}[/red]")
        return False
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")

if __name__ == "__main__":
    typer.run(init_db)