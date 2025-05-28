# reset.py
from rich import print
import psycopg2
from psycopg2 import Error
import os


def run_reset(db_config):
    """只重置数据库（删除并重建）"""
    _reset_db(db_config,restore_schema=False)

def run_reset_with_schema(db_config):
    """重置数据库后自动导入 schema.sql"""
    _reset_db(db_config,restore_schema=True)

def _reset_db(db_config,restore_schema: bool):
    try:
        print(f"[blue]正在连接到 postgres 数据库以重置目标库 {db_config['database']}...[/blue]")
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 杀掉目标数据库的连接
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_config["database"]}' AND pid <> pg_backend_pid();
        """)

        # 删除并重建数据库
        cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
        cursor.execute(f"CREATE DATABASE {db_config['database']}")
        print(f"[green]数据库 {db_config['database']} 已重置。[/green]")

    except Error as e:
        print(f"[red]数据库重置失败: {e}[/red]")
        return
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()

    # 可选：导入 schema.sql
    if restore_schema:
        _import_schema_sql(db_config)

def _import_schema_sql(db_config):
    try:
        print("[blue]正在导入 schema.sql 文件...[/blue]")

        if not os.path.exists("schema.sql"):
            print("[red]未找到 schema.sql 文件，请确认文件位于项目根目录。[/red]")
            return

        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        print("[green]schema.sql 导入成功！[/green]")

    except Error as e:
        print(f"[red]导入 schema.sql 失败: {e}[/red]")
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()
            print("[blue]数据库连接已关闭[/blue]")
