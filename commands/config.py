# 2025/5/27 10:54
# config.py
import os
import json
from psycopg2 import OperationalError
import psycopg2
from rich import print
import getpass
from rich.panel import Panel

os.environ["PYTHONIOENCODING"] = "utf-8"
CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": int(123),
    "database": "project2025"
}

def show_help():
    help_text = """[bold bright_cyan]欢迎使用 SQL 交互式查询工具！[/bold bright_cyan]

[bold bright_green]基本用法：[/bold bright_green]
- 输入标准 SQL 语句（以分号结尾）执行查询，例如：
  [bright_white on bright_black]SELECT * FROM users;[/bright_white on bright_black]

- 输入自然语言提问（以问号开头），自动生成 SQL 并执行：
  [bright_white on bright_black]? 查询所有用户的姓名和邮箱；[/bright_white on bright_black]

[bold bright_magenta]特殊指令（以 / 开头）：[/bold bright_magenta]
- [bold]/reset;[/bold]         重置数据库（清空数据但保留关系）
- [bold]/reset_demo;[/bold]   重置数据库并导入 schema.sql 示例结构
- [bold]/_init;[/bold] 或 [bold]/l;[/bold]   查看当前数据库中的所有表及记录数
- [bold]/config_reset;[/bold]  重新设置数据库连接配置
- [bold]/status;[/bold]        查看当前数据库连接状态
- [bold]/schema;[/bold]        查看当前数据库结构
- [bold]/help;[/bold]          显示本帮助信息

[bold bright_blue]退出方式：[/bold bright_blue]
- 输入 [bold]exit;[/bold] 或 [bold]quit;[/bold] 即可退出

[bold cyan]更多信息请：[/bold cyan]
[link=https://github.com/Liu-Z-C/psql-homework][bold cyan]跳转至GitHub仓库[/bold cyan][/link]

[bright_red]祝你使用愉快！[/bright_red]"""
    print(Panel(help_text, title="使用帮助", subtitle="你可以随时输入 /help; 查看"))

def config_exists():
    return os.path.exists(CONFIG_PATH) and os.path.getsize(CONFIG_PATH) > 0

def load_config(verbose: bool = False):
    if config_exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            if verbose:
                safe_config = config.copy()
                if 'password' in safe_config:
                    safe_config['password'] = '****'
                print(f"[bright_green]已加载数据库配置：{safe_config}[/bright_green]")

            # ✅ 测试连接有效性
            test_db_connection(config)
            return config
    else:
        config = setup_config()
        test_db_connection(config)  # 同样测试首次配置
        return config

def setup_config():
    print("[bright_yellow]首次使用，请输入数据库连接信息：[/bright_yellow]")
    config = {}
    config["host"] = input("数据库主机地址 [localhost]: ") or "localhost"
    config["port"] = int(input("数据库端口 [5432]: ") or "5432")
    config["user"] = input("数据库用户名 [postgres]: ") or "postgres"
    config["password"] = getpass.getpass("数据库密码: ")
    config["database"] = input("数据库名 [project2025]: ") or "project2025"

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        print("[bright_green]配置已保存到 config.json[/bright_green]")
    show_help()
    return config

def reset_config():
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
    print("[red]配置已清除，请重新设置连接信息。[/red]")
    return setup_config()

def test_db_connection(config: dict, verbose: bool = False) -> bool:
    try:
        conn = psycopg2.connect(**config)
        conn.close()
        if verbose:
            print("[bright_green]✓ 数据库连接成功[/bright_green]")
        return True

    except Exception as e:  # 不仅捕获 psycopg2 的 OperationalError
        if verbose:
            print(f"[red]✗ 无法连接数据库：{e}[/red]")

            msg = str(e).lower()
            if "does not exist" in msg:
                print("[yellow]可能原因：数据库不存在，请确认 database 名。[/yellow]")
            elif ("authentication failed"in msg) or ("no password supplied"in msg):
                print("[yellow]可能原因：用户名或密码错误。[/yellow]")
            elif "connection refused" in msg:
                print("[yellow]可能原因：数据库未启动或端口错误。[/yellow]")
            elif "timeout expired" in msg:
                print("[yellow]可能原因：连接超时，检查网络或主机地址。[/yellow]")
            elif "codec can't decode" in msg:
                print("[yellow]可能原因：编码错误/数据库不存在[/yellow]")
            else:
                print("[yellow]未知错误，请检查连接参数和服务器设置。[/yellow]")

        return False
