# SQL 交互式查询工具 [![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3130/)

一个基于 Python 的终端 SQL 交互系统，支持：

- [x] 输入标准 SQL 并执行
- [x] 简单的自动补全
- [x] 使用自然语言生成 SQL 查询（集成通义千问）
- [x] 快速查看数据库结构、重置数据库
- [x] 含打包的可执行文件，双击即可运行

---

## 📦 使用方式

### ✅ 方式一：运行 Python 项目

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 启动主程序：

   ```bash
   python main.py
   ```

3. 首次运行会引导配置数据库连接信息，配置将保存在 `config.json` 中。

---

### ✅ 方式二：使用打包好的程序

1. 在`Release`中找到已打包的 `pgtool`

2. 双击运行，进入交互界面

3. 同样会提示输入数据库连接信息，并保存到本地 `config.json`

---

## 🚀 基本用法

* 执行标准 SQL（必须以分号结尾）：

  ```
  SELECT * FROM users;
  ```

* 使用自然语言提问（以问号开头）：

  ```
  ? 查询所有用户的邮箱；
  ```

系统会自动生成 SQL 查询并执行。

---

## ⚙️ 特殊命令说明

| 指令                | 功能描述                     |
| ----------------- | ------------------------ |
| `/reset;`         | 重置数据库（清空所有数据）            |
| `/reset_demo;`    | 重置数据库并执行 `schema.sql` 导入 |
| `/_init;` 或 `/l;` | 显示数据库中所有表及记录数            |
| `/config_reset;`  | 重新设置数据库连接                |
| `/status;`          | 查看当前数据库连接状态           |
| `/schema;`          |    查看当前数据库结构        |
| `/help;`          | 显示帮助信息                   |
| `exit;` 或 `quit;` | 退出程序                     |

---

## 🔐 配置说明（config.json）

系统会自动生成 `config.json` 保存数据库连接信息：

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "******",
  "database": "project2025"
}
```

---

## 🤖 自然语言 SQL 生成功能

* 集成 [通义千问](https://bailian.console.aliyun.com/?utm_content=se_1021227512&tab=api#/api/?type=model&url=https%3A%2F%2Fhelp.aliyun.com%2Fdocument_detail%2F2712576.html&renderType=iframe) 生成 SQL
* 自动读取项目根目录下的 `schema.sql` 文件作为数据库结构
* 返回查询结果并格式化展示

---

## 🧱 技术栈

* prompt\_toolkit
* rich
* psycopg2
* OpenAI SDK

---

## 📄 License

[MIT License © 2025](https://github.com/746505972/psql-homework/blob/main/LICENSE)

