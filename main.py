# main.py
from prompt_toolkit import PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from rich import print

from commands import run_query, load_config
from commands.config import show_help


@Condition
def custom_is_multiline() -> bool:
    doc: Document = get_app().current_buffer.document
    text = doc.text.strip()
    return not text.endswith(';')

def interactive_shell():
    print("[bright_red]SQL交互式控制台 (输入[bright_yellow]exit[/bright_yellow]退出)[/bright_red]")
    print("[bright_red]输入SQL语句并以分号([bright_yellow];[/bright_yellow])结尾，然后按回车执行[/bright_red]")
    print("[bright_red]以问号开头输入自然语言[/bright_red]")

    # 提示数据库参数
    load_config(verbose=True)

    sql_completer = WordCompleter([
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
        'CREATE', 'DROP', 'ALTER', 'JOIN','NATURAL JOIN', 'GROUP BY', 'ORDER BY',
        'LIMIT', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN','LANGUAGE','HAVING',
        'energy_consumption','automation_rules','user_feedback','security_events','usage_logs',
        'device_status_history','devices','rooms','user_home_assignments','homes','users',
        'exit;','quit;','/reset_config;','/reset;','/_init;','/l;','/reset_demo;','/h;','/help;'
    ], ignore_case=True)

    session = PromptSession(
        history=FileHistory('.sql_history'),
        auto_suggest=AutoSuggestFromHistory(),
        completer=sql_completer,
        multiline=custom_is_multiline
    )

    while True:
        try:
            user_input = session.prompt('SQL> ')
            raw = user_input.strip()

            # 判断是否退出（支持 exit; 或 quit;，中英文分号）
            if raw.lower().rstrip(';；') in ('exit', 'quit'):
                break

            # 检查是否以中英文分号结尾
            if raw.endswith(';') or raw.endswith('；'):
                # 去除结尾分号和两端空格
                command = raw.rstrip(';；').strip()

                # 处理：以 / 开头的特殊命令
                if command.startswith('/'):
                    cmd = command.lower()
                    if cmd == '/reset_demo':
                        from commands.reset import run_reset_with_schema
                        run_reset_with_schema()
                    elif cmd == '/reset':
                        from commands.reset import run_reset
                        run_reset()
                    elif cmd in ('/_init', '/l'):
                        from commands.db_init import run_init_check
                        run_init_check()
                    elif cmd in ('/config_reset', '/reset_config'):
                        from commands.config import reset_config
                        reset_config()
                    elif cmd in ('/h', '/help'):
                        show_help()
                    else:
                        print(f"[yellow]未知命令：{cmd}[/yellow]")

                # 处理：自然语言命令
                elif command.startswith('?') or command.startswith('？'):
                    from commands.nlp_query import run_nlp_query
                    question = command[1:].strip()
                    run_nlp_query(question)

                # 处理：SQL 正常语句
                else:
                    run_query(command)

            else:
                print("[yellow]提示: SQL语句应以英文或中文分号结尾（; 或 ；）。输入'exit;'退出。[/yellow]")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"[red]错误: {e}[/red]")


if __name__ == "__main__":
    interactive_shell()
