# 后端生产环境Dockerfile
FROM python:3.10-slim-bullseye

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 升级pip
RUN pip install --no-cache-dir --upgrade pip

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传文件目录
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=manage.py
ENV PYTHONUNBUFFERED=1

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "50", "manage:app"]