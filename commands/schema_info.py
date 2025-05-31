import psycopg2

def get_schema_from_db(config: dict, styled: bool = False) -> str:
    """
    根据 config 获取数据库结构（表 + 字段 + 类型）。
    
    参数:
        styled: 是否使用 rich 样式（用于命令行显示）

    返回:
        str（样式化或普通结构）
    """
    try:

        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        schema_lines = []

        for table in tables:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table,))
            columns = cursor.fetchall()

            if styled:
                column_defs = ", ".join([f"[cyan]{col}[/cyan] [magenta]{dtype}[/magenta]" for col, dtype in columns])
                schema_lines.append(f"[bold bright_yellow]表 {table}([/bold bright_yellow] [white]{column_defs}[/white][bold bright_yellow])[/bold bright_yellow]")
            else:
                column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns])
                schema_lines.append(f"表 {table} ({column_defs})")

        cursor.close()
        conn.close()
        return "\n".join(schema_lines)

    except Exception as e:
        return f"无法获取数据库结构: {str(e)}"
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()

