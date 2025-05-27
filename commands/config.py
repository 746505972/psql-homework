# 2025/5/27 10:54
# config.py
import os
import json
from rich import print

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": int(123),
    "database": "project2025"
}

def config_exists():
    return os.path.exists(CONFIG_PATH) and os.path.getsize(CONFIG_PATH) > 0

def load_config(verbose:bool=False):
    if config_exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            print(f"[bright_green]已加载数据库配置：{config}[/bright_green]") if verbose else None
            return config
    else:
        return setup_config()

def setup_config():
    print("[yellow]首次使用，请输入数据库连接信息：[/yellow]")
    config = {}
    config["host"] = input("数据库主机地址 [localhost]: ") or "localhost"
    config["port"] = int(input("数据库端口 [5432]: ") or "5432")
    config["user"] = input("数据库用户名 [postgres]: ") or "postgres"
    config["password"] = input("数据库密码: ")
    config["database"] = input("数据库名 [project2025]: ") or "project2025"

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        print("[bright_green]配置已保存到 config.json[/bright_green]")
    return config

def reset_config():
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
    print("[red]配置已清除，请重新设置连接信息。[/red]")
    return setup_config()
