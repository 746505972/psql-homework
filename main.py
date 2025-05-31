# main.py
from prompt_toolkit import PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from rich import print

from commands import run_query, load_config, test_db_connection
from commands.completion import SQLSmartCompleter
from commands.config import show_help


@Condition
def custom_is_multiline() -> bool:
    doc: Document = get_app().current_buffer.document
    text = doc.text.strip()
    return not text.endswith(';') and not text.endswith('；')


def interactive_shell():
    print("[bright_red]SQL交互式控制台 (输入[bright_yellow]exit[/bright_yellow]退出)[/bright_red]")
    print("[bright_red]输入SQL语句并以分号([bright_yellow];[/bright_yellow])结尾，然后按回车执行[/bright_red]")
    print("[bright_red]以问号开头输入自然语言[/bright_red]")

    # 加载配置并测试连接
    config = load_config(verbose=True)
    config_valid = test_db_connection(config, verbose=True)

    # 即使连接失败也允许进入交互界面
    sql_completer = SQLSmartCompleter(config if config_valid else {})

    session = PromptSession(
        history=FileHistory('.sql_history'),
        auto_suggest=AutoSuggestFromHistory(),
        completer=sql_completer,
        multiline=custom_is_multiline
    )

    while True:
        try:
            prompt_color = 'ansimagenta' if config_valid else 'ansired'
            user_input = session.prompt(HTML(f'<{prompt_color}><b>SQL>>></b></{prompt_color}> '))
            raw = user_input.strip()

            if raw.lower().rstrip('；;') in ('exit', 'quit'):
                break

            if raw.endswith(';') or raw.endswith('；'):
                command = raw.rstrip('；;').strip()

                if command.startswith('/'):
                    cmd = command.lower()

                    if cmd == '/reset_demo':
                        if config_valid:
                            from commands.reset import run_reset_with_schema
                            run_reset_with_schema(config)
                        else:
                            print("[red]数据库配置无效，请先使用 /config_reset 修复[/red]")

                    elif cmd == '/reset':
                        if config_valid:
                            from commands.reset import run_reset
                            run_reset(config)
                        else:
                            print("[red]数据库配置无效，请先使用 /config_reset 修复[/red]")

                    elif cmd in ('/_init', '/l'):
                        if config_valid:
                            from commands.db_init import run_init_check
                            run_init_check(config)
                        else:
                            print("[red]数据库配置无效，请先使用 /config_reset 修复[/red]")

                    elif cmd == '/schema':
                        if config_valid:
                            from commands.schema_info import get_schema_from_db
                            schema = get_schema_from_db(config, styled=True)
                            print(f"[green]当前数据库结构:\n{schema}[/green]")
                        else:
                            print("[red]数据库配置无效，请先使用 /config_reset 修复[/red]")

                    elif cmd in ('/config_reset', '/reset_config'):
                        from commands.config import reset_config
                        config = reset_config()
                        config_valid = test_db_connection(config, verbose=True)
                        
                    elif cmd == '/status':
                        """判断当前离线/在线"""
                        if config_valid:
                            print("[green]当前数据库配置有效，连接正常。[/green]")
                        else:
                            print("[red]当前数据库配置无效，连接失败。[/red]")

                    elif cmd in ('/h', '/help'):
                        show_help()

                    else:
                        print(f"[yellow]未知命令：{cmd}[/yellow]")

                elif command.startswith('?') or command.startswith('？'):
                    if config_valid:
                        from commands.nlp_query import run_nlp_query
                        question = command[1:].strip()
                        run_nlp_query(question, config)
                    else:
                        print("[red]当前数据库配置无效，自然语言查询不可用。请先运行 /config_reset[/red]")

                else:
                    if config_valid:
                        run_query(command, config)
                    else:
                        print("[red]数据库配置无效，无法执行 SQL 查询。请先运行 /config_reset[/red]")

            else:
                print("[yellow]提示: SQL语句应以英文或中文分号结尾（; 或 ；）。输入 'exit;' 退出。[/yellow]")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"[red]错误: {e}[/red]")



if __name__ == "__main__":
    interactive_shell()
