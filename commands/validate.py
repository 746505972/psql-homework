import typer
from rich import print
from rich.panel import Panel
import sqlparse
import psycopg2
from psycopg2 import Error
from openai import OpenAI
import os
import json
from typing import Optional

def get_ai_analysis(query: str, error_msg: Optional[str] = None) -> str:
    """使用通义千问分析SQL查询"""
    try:
        client = OpenAI(
            api_key="sk-6d39a5e677c346c5806bea72b523a6cb",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 构建提示信息
        if error_msg:
            prompt = f"""作为SQL专家，请分析以下SQL查询的错误并提供修正建议：
            
SQL查询: {query}
错误信息: {error_msg}

请提供：
1. 错误原因的详细分析
2. 具体的修正建议
3. 正确的SQL示例

请用通俗易懂的中文回答。"""
        else:
            prompt = f"""作为SQL专家，请分析以下SQL查询的结构并提供优化建议：
            
SQL查询: {query}

请提供：
1. 查询结构分析
2. 性能优化建议
3. 可能的改进示例
4.不要写总结
请用通俗易懂的中文回答。"""

        completion = client.chat.completions.create(
            model="qwen-turbo-latest",
            messages=[
                {'role': 'system', 'content': '你是一个经验丰富的SQL专家，擅长分析SQL查询并提供优化建议。'},
                {'role': 'user', 'content': prompt}
            ]
        )
        
        # 解析返回的JSON响应
        response = json.loads(completion.model_dump_json())
        return response['choices'][0]['message']['content']
        
    except Exception as e:
        return f"AI分析失败: {str(e)}\n请检查API密钥设置或网络连接。"

def check_query(
    query: str = typer.Argument(..., help="要执行的SQL查询语句"),
    host: str = typer.Option("localhost", help="数据库主机地址"),
    port: str = typer.Option("5432", help="数据库端口"),
    user: str = typer.Option('postgres', prompt=True, help="数据库用户名"),
    password: str = typer.Option("LZClzc0712!", prompt=True, hide_input=True, help="数据库密码"),
    database: str = "project2025"
):
    """检查SQL查询语句的正确性并提供AI分析"""
    try:
        # 格式化SQL
        formatted = sqlparse.format(query, reindent=True, keyword_case='upper')
        
        # 连接数据库进行语法验证
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # 使用EXPLAIN来验证查询语法
        try:
            cursor.execute(f"EXPLAIN {query}")
            print(Panel("[green]✓ SQL语句格式正确![/green]", title="验证结果"))
            print(Panel(formatted, title="格式化后的SQL"))
            
            # 显示执行计划
            plan = cursor.fetchall()
            print(Panel("\n".join([line[0] for line in plan]), title="执行计划"))
            
            # 获取AI优化建议
            ai_analysis = get_ai_analysis(query)
            print(Panel(ai_analysis, title="AI 分析与优化建议"))
                
        except Error as e:
            error_msg = str(e)
            print(Panel(f"[red]✗ SQL语句存在错误:[/red]\n{error_msg}", title="错误信息"))
            
            # 获取AI错误分析和修正建议
            ai_suggestion = get_ai_analysis(query, error_msg)
            print(Panel(ai_suggestion, title="AI 错误分析与修正建议"))
            
    except Error as e:
        print(Panel(f"[red]验证过程中出错: {str(e)}[/red]", title="错误"))
    finally:
        if 'conn' in locals() and not conn.closed:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    typer.run(check_query)