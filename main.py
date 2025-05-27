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

@Condition
def custom_is_multiline() -> bool:
    doc: Document = get_app().current_buffer.document
    text = doc.text.strip()
    return not text.endswith(';')

def interactive_shell():
    print("[bright_red]SQL交互式控制台 (输入[bright_yellow]exit[/bright_yellow]退出)[/bright_red]")
    print("[bright_red]输入SQL语句并以分号([bright_yellow];[/bright_yellow])结尾，然后按回车执行[/bright_red]")

    # 提示数据库参数
    load_config(verbose=True)

    sql_completer = WordCompleter([
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
        'CREATE', 'DROP', 'ALTER', 'JOIN', 'GROUP BY', 'ORDER BY',
        'LIMIT', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN','energy_consumption',
        'automation_rules','user_feedback','security_events','usage_logs','device_status_history',
        'devices','rooms','user_home_assignments','homes','users','exit;','quit;','reset_config;','reset;',
        '_init;','/l;','reset_demo;'
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
            if user_input.lower().strip(';') in ('exit', 'quit'):
                break
            if user_input.strip().endswith(';'):
                sql = user_input.rstrip(';').strip()
                if sql.lower() in "reset_demo":
                    from commands.reset import run_reset_with_schema
                    run_reset_with_schema()
                elif sql.lower() == 'reset':
                    from commands.reset import run_reset
                    run_reset()
                elif sql.lower() in ('_init', '/l'):
                    from commands.db_init import run_init_check
                    run_init_check()
                elif sql.lower() == 'config_reset' or sql.lower() == 'reset_config':
                    from commands.config import reset_config
                    reset_config()
                elif sql.startswith('?') or sql.startswith('？'):
                    from commands.nlp_query import run_nlp_query
                    question = sql[1:].strip()
                    run_nlp_query(question)
                else:
                    run_query(sql)
            else:
                print("提示: SQL语句应以分号(;)结尾。请继续输入或输入'exit'退出")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"错误: {e}")
            break

if __name__ == "__main__":
    interactive_shell()
