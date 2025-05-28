# db_init.py
import psycopg2
from psycopg2 import Error
from rich import print

def run_init_check(db_config):
    """列出数据库中的所有表及其记录数"""
    try:
        print(f"[blue]正在连接到数据库 {db_config['database']}...[/blue]")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()

        if not tables:
            print("[yellow]当前数据库中没有任何表。[/yellow]")
        else:
            print("\n[green]数据库中的表:[/green]")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cursor.fetchone()
                count = result[0] if result is not None else 0
                print(f"[bright_cyan]- {table_name}: [yellow]{count}[/yellow] 条记录[/bright_cyan]")

            print("\n[green]数据库结构验证完成！[/green]")

    except Error as e:
        print(f"[red]数据库连接失败: {str(e)}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")
