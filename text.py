# 2025/5/27 11:51
from rich import print

for name in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
             "bright_black", "bright_red", "bright_green", "bright_yellow",
             "bright_blue", "bright_magenta", "bright_cyan", "bright_white"]:
    print(f"[{name}]{name:<16} 示例文字 [{name}]")
