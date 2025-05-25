# Conmmand命令
commands文件夹中记录了六个命令，分别是：\
init：初始化数据库；\
query：sql语句查询；\
nlp_query(实际上main.py调用的时候将命令简化为nlp)；\
reset：清除系统;\
validate：检查报错并给出AI建议;\
visualize：可视化查询;
# 使用方法
1. 创建虚拟环境（python3.11.11）
2. 下载requirement中的库
3. 构建数据库project2025，运行schema.sql中的命令
4. 打开Anaconda命令行，首先激活该虚拟环境，然后定位到项目main.py的目录下，接下来在命令行输入
5. 输入为：例如python main.py query "SELECT * FROM devices"
