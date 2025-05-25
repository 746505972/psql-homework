import typer
from commands import db_init, query, validate, visualize, reset,nlp_query

app = typer.Typer(
    name="sql-tool",
    help="SQL查询分析与可视化工具"
)

# 注册子命令
app.command('init')(db_init.init_db)
app.command('query')(query.execute_query)
app.command('validate')(validate.check_query)
app.command('visualize')(visualize.visualize_query)
app.command('reset')(reset.reset_db)
app.command('nlp')(nlp_query.natural_query)

if __name__ == "__main__":
    app()