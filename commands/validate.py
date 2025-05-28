import json
from typing import Optional

from openai import OpenAI


def get_ai_analysis(query: str, error_msg: Optional[str] = None) -> str:
    """使用通义千问分析SQL查询"""
    try:
        client = OpenAI(
            api_key="sk-6d39a5e677c346c5806bea72b523a6cb",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 构建提示信息
        if error_msg:
            prompt = f"""作为SQL命令行工具内置AI助手，请分析以下SQL查询的错误并提供修正建议：
            
SQL查询: {query}
错误信息: {error_msg}

请做到简洁的回复：
1. 错误原因的分析
2. 具体的修正建议
3. 正确的SQL示例

请用通俗易懂的中文回答。"""
        else:
            prompt = f"""作为SQL命令行工具内置AI助手，请分析以下SQL查询的结构并提供优化建议：
            
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
