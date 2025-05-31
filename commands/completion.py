# 2025/5/28 19:51
from prompt_toolkit.completion import Completer, Completion
import psycopg2

class SQLSmartCompleter(Completer):
    def __init__(self, config: dict):
        self.keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'JOIN', 'NATURAL JOIN',
            'GROUP BY', 'ORDER BY', 'LIMIT', 'HAVING',
            'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL'
        ]

        self.meta_commands = [
            '/reset;', '/reset_demo;', '/l;', '/_init;',
            '/reset_config;', '/config_reset;', '/help;','/h;',
            '/test;', '/status;', 'exit;', 'quit;','/schema;'
        ]

        self.table_names = []
        self.column_names = {}  # 表名 -> [字段1, 字段2]
        self.schema_loaded = False

        # 尝试连接数据库加载结构（允许失败）
        if config and isinstance(config, dict):
            self._load_schema(config)

    def _load_schema(self, config):
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            self.table_names = [row[0] for row in cursor.fetchall()]

            for table in self.table_names:
                cursor.execute(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = %s
                """, (table,))
                self.column_names[table] = [row[0] for row in cursor.fetchall()]

            cursor.close()
            conn.close()
            self.schema_loaded = True

        except Exception as e:
            print(f"[red]自动补全初始化失败: {e}[/red]")

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        last_word = text.split()[-1] if text.split() else ''

        # 判断是否在 SELECT 后
        if 'select' in text and 'from' not in text:
            for table, columns in self.column_names.items():
                for col in columns:
                    if col.startswith(last_word):
                        yield Completion(col, start_position=-len(last_word))
            return

        # 表名补全（FROM 或 JOIN 后）
        if 'from' in text or 'join' in text:
            for table in self.table_names:
                if table.startswith(last_word):
                    yield Completion(table, start_position=-len(last_word))
            return

        # 默认关键字 + 表名 + 命令补全
        for word in self.keywords + self.table_names + self.meta_commands:
            if word.lower().startswith(last_word):
                yield Completion(word, start_position=-len(last_word))
