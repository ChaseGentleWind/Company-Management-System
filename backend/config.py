import os
from dotenv import load_dotenv
from datetime import timedelta # <-- 1. 导入 timedelta

# 直接加载 .env 文件，python-dotenv 会自动在工作目录中寻找
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

# 2. 新增下面这行，将 Access Token 的有效期设置为 1 小时
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # SQLAlchemy 配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DATABASE')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False