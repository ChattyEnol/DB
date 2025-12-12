# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 初始化数据库
RUN python init_db.py

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "app.py"]