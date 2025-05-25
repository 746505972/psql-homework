import typer
from rich import print
import graphviz
import sqlparse
import os
from sqlparse.sql import Identifier, IdentifierList, TokenList
from sqlparse.tokens import Keyword, DML, Punctuation

# 图形样式定义
CLAUSE_STYLES = {
    "SELECT": {"shape": "ellipse", "fillcolor": "lightgreen"},  # 选择子句：椭圆形，浅绿色
    "FROM": {"shape": "ellipse", "fillcolor": "skyblue"},      # FROM子句：椭圆形，天蓝色
    "WHERE": {"shape": "parallelogram", "fillcolor": "lightcoral"}, # WHERE子句：平行四边形，浅珊瑚色
    "JOIN": {"shape": "cds", "fillcolor": "lightyellow"},      # 连接子句：CD形状，浅黄色
    "LEFT JOIN": {"shape": "cds", "fillcolor": "lightyellow"},
    "RIGHT JOIN": {"shape": "cds", "fillcolor": "lightyellow"},
    "INNER JOIN": {"shape": "cds", "fillcolor": "lightyellow"},
    "FULL OUTER JOIN": {"shape": "cds", "fillcolor": "moccasin"},
    "GROUP BY": {"shape": "octagon", "fillcolor": "lightpink"}, # 分组子句：八边形，浅粉色
    "HAVING": {"shape": "octagon", "fillcolor": "lightsalmon"}, # HAVING子句：八边形，浅橙色
    "ORDER BY": {"shape": "septagon", "fillcolor": "lightgoldenrodyellow"}, # 排序子句：七边形，浅金色
    "LIMIT": {"shape": "trapezium", "fillcolor": "lightcyan"},  # LIMIT子句：梯形，浅青色
    "DEFAULT": {"shape": "ellipse", "fillcolor": "lightgrey"}   # 默认样式：椭圆形，浅灰色
}

# 表格节点样式
TABLE_STYLE = {
    "shape": "box3d",          # 3D盒子形状
    "style": "filled",         # 填充样式
    "fillcolor": "lightblue",  # 填充颜色：浅蓝
    "fontname": "Arial"        # 字体
}

# 根查询节点样式
ROOT_QUERY_STYLE = {
    "shape": "doubleoctagon",  # 双八边形
    "style": "filled",         # 填充样式
    "fillcolor": "gray80",     # 填充颜色：灰色
    "fontname": "Arial Black"  # 字体
}

def _extract_clause_details(tokens, max_len=50):
    """从令牌列表中提取摘要字符串用于节点标签"""
    details = []
    current_length = 0
    for t in tokens:
        if t.is_whitespace:
            continue
        s = str(t)
        if current_length + len(s) > max_len:
            details.append("...")
            break
        details.append(s)
        current_length += len(s) + 1  # +1 用于空格
    return " ".join(details).strip()

def _get_involved_tables_from_tokens(tokens):
    """从令牌列表中提取表名（通常在FROM/JOIN之后）"""
    tables = []
    for token in tokens:
        if isinstance(token, Identifier):
            tables.append(token.get_real_name())
        elif isinstance(token, IdentifierList):
            for ident in token.get_identifiers():
                if isinstance(ident, Identifier):
                    tables.append(ident.get_real_name())
    return list(set(tables))  # 返回去重后的表名列表

def check_graphviz():
    """检查 Graphviz 是否正确安装并设置环境变量"""
    # 常见的 Graphviz 安装路径
    common_paths = [
        r"C:\Program Files\Graphviz\bin",
        r"C:\Program Files (x86)\Graphviz\bin",
        r"C:\Graphviz\bin"
    ]
    
    dot_exe = 'dot.exe'
    
    # 首先检查环境变量PATH中的路径
    for path in os.environ.get('PATH', '').split(os.pathsep):
        dot_path = os.path.join(path, dot_exe)
        if os.path.exists(dot_path):
            return True
    
    # 检查常见安装路径
    for path in common_paths:
        dot_path = os.path.join(path, dot_exe)
        if os.path.exists(dot_path):
            # 找到dot.exe后，临时添加到环境变量
            os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
            return True
    
    return False

def visualize_query(
    query: str = typer.Argument(..., help="需要可视化的SQL查询语句"),
    output_filename: str = typer.Option("query_visualization", help="输出文件名（不含扩展名）")
):
    """将SQL查询语句可视化为流程图"""
    try:
        # 首先检查 Graphviz 是否可用
        if not check_graphviz():
            print("[red]错误：未找到 Graphviz 的 'dot' 可执行文件[/red]")
            print("[yellow]请按照以下步骤操作：[/yellow]")
            print("1. 下载并安装 Graphviz：https://graphviz.org/download/")
            print("2. 将 Graphviz 安装目录下的 bin 文件夹添加到系统环境变量PATH中")
            print("3. 重新运行此命令")
            print("\n[yellow]常见安装位置：[/yellow]")
            print("- C:\\Program Files\\Graphviz\\bin")
            print("- C:\\Program Files (x86)\\Graphviz\\bin")
            print("- C:\\Graphviz\\bin")
            return False

        # 检查输入的SQL语句是否为空
        if not query.strip():
            print("[yellow]警告：输入的查询语句为空[/yellow]")
            return False

        # 使用sqlparse解析SQL查询
        parsed_list = sqlparse.parse(query)
        if not parsed_list:
            print("[red]错误：无法解析SQL查询语句[/red]")
            return False
        
        parsed = parsed_list[0]  # 获取第一个语句

        # 创建图形对象，设置字体和编码
        dot = graphviz.Digraph(comment='SQL查询结构', engine='dot',
                              encoding='utf-8')
        
        # 设置图形全局属性
        dot.attr(rankdir='TB',
                label=f'SQL查询语句: {query[:30]}...' if len(query)>30 else f'SQL查询语句: {query}',
                labelloc='t',
                fontsize='20',
                fontname="Microsoft YaHei",  # 使用中文字体
                charset='utf-8')
        
        # 设置节点默认属性
        dot.attr('node', fontname="Microsoft YaHei")
        # 设置边默认属性
        dot.attr('edge', fontname="Microsoft YaHei")

        # --- 第一遍扫描：识别并创建表节点 ---
        table_node_ids = {}  # 存储表名到节点ID的映射
        
        # 遍历所有令牌查找表标识符
        q_tokens = parsed.tokens
        i = 0
        while i < len(q_tokens):
            token = q_tokens[i]
            # 表名通常出现在FROM或JOIN关键字之后
            if token.ttype is Keyword and (token.value.upper() == 'FROM' or 'JOIN' in token.value.upper()):
                j = i + 1
                temp_table_tokens = []
                # 收集直到下一个主要关键字的所有标识符
                while j < len(q_tokens):
                    sub_token = q_tokens[j]
                    if isinstance(sub_token, Identifier) or isinstance(sub_token, IdentifierList):
                        temp_table_tokens.append(sub_token)
                    # 遇到新的主要关键字或非逗号标点时停止
                    elif sub_token.ttype is Keyword and sub_token.value.upper() not in ('AS'):
                        break
                    elif sub_token.ttype is Punctuation and str(sub_token) != ',':
                        break
                    j += 1
                
                # 提取表名并创建节点
                extracted_tables = _get_involved_tables_from_tokens(temp_table_tokens)
                for table_name in extracted_tables:
                    if table_name not in table_node_ids:
                        node_id = f"tbl_{table_name.replace('.', '_')}"  # 处理schema.table格式
                        table_node_ids[table_name] = node_id
                        dot.node(node_id, f"TABLE\n{table_name}", **TABLE_STYLE)
            i += 1
            
        # --- 第二遍扫描：处理SQL子句并建立连接 ---
        root_node_id = "sql_query_root"
        dot.node(root_node_id, "SQL Query", **ROOT_QUERY_STYLE)
        previous_clause_node_id = root_node_id
        
        # 遍历令牌处理主要SQL子句
        idx = 0
        while idx < len(parsed.tokens):
            token = parsed.tokens[idx]
            
            if token.is_whitespace:
                idx += 1
                continue

            # 识别SQL关键字
            is_clause_keyword = False
            keyword_value = ""

            # 处理SELECT关键字
            if token.ttype is DML and token.value.upper() == 'SELECT':
                is_clause_keyword = True
                keyword_value = 'SELECT'
            # 处理其他关键字
            elif token.ttype is Keyword:
                # 处理复合关键字（如GROUP BY, ORDER BY等）
                current_keyword_parts = [token.value.upper()]
                k = idx + 1
                while k < len(parsed.tokens):
                    next_token = parsed.tokens[k]
                    if next_token.is_whitespace:
                        k += 1
                        continue
                    # 检查是否是复合关键字的后半部分
                    if (current_keyword_parts[-1] in ('GROUP', 'ORDER') and next_token.value.upper() == 'BY') or \
                       (current_keyword_parts[-1] in ('LEFT', 'RIGHT', 'INNER', 'FULL') and 'JOIN' in next_token.value.upper()):
                        current_keyword_parts.append(next_token.value.upper())
                        idx = k
                    else:
                        break
                    k += 1
                
                keyword_value = " ".join(current_keyword_parts)

                # 检查是否是主要子句关键字
                if keyword_value in ('FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT') or \
                   'JOIN' in keyword_value:
                    is_clause_keyword = True
            
            # 处理找到的子句关键字
            if is_clause_keyword:
                clause_node_id = f"clause_{keyword_value.replace(' ','_').lower()}_{idx}"
                
                # 提取子句详情
                details_tokens = []
                j = idx + 1
                while j < len(parsed.tokens):
                    next_t = parsed.tokens[j]
                    if (next_t.ttype is DML and next_t.value.upper() == 'SELECT') or \
                       (next_t.ttype is Keyword and \
                        (next_t.value.upper() in ('FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT') or 'JOIN' in next_t.value.upper())):
                        break
                    if not next_t.is_whitespace:
                        if not (keyword_value.count(' ') > 0 and str(next_t) in keyword_value.split()):
                            details_tokens.append(next_t)
                    j += 1
                
                # 创建节点标签
                clause_details_str = _extract_clause_details(details_tokens)
                node_label = f"{keyword_value}\n({clause_details_str})" if clause_details_str else keyword_value
                
                # 应用节点样式
                base_keyword_for_style = keyword_value.split()[0] if 'JOIN' in keyword_value else keyword_value
                style_attrs = CLAUSE_STYLES.get(keyword_value, CLAUSE_STYLES.get(base_keyword_for_style, CLAUSE_STYLES["DEFAULT"]))
                
                # 添加节点和边
                dot.node(clause_node_id, node_label, **style_attrs)
                dot.edge(previous_clause_node_id, clause_node_id)
                previous_clause_node_id = clause_node_id

                # 为FROM和JOIN子句添加到表的连接
                if keyword_value == 'FROM' or 'JOIN' in keyword_value:
                    involved_tables = _get_involved_tables_from_tokens(details_tokens)
                    for table_name in involved_tables:
                        if table_name in table_node_ids:
                            dot.edge(clause_node_id, table_node_ids[table_name], 
                                   style="dashed", color="gray50", 
                                   arrowhead="odot", label="访问")
            
            idx += 1

        # 生成并保存图形
        output_path_full = os.path.join(os.getcwd(), output_filename)
        dot.render(output_path_full, format='png', cleanup=True)
        print(f"[green]📊 查询可视化已保存为 {output_path_full}.png[/green]")
        return True

    except Exception as e:
        print(f"[red]❌ 可视化失败：{str(e)}[/red]")
        return False

if __name__ == "__main__":
    typer.run(visualize_query)