from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化插件
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # 允许所有来源跨域访问/api/下的路径

    # 注册蓝图
    from .api.auth import auth_bp
    from .api.users import users_bp
    from .api.orders import orders_bp
    from .api.notifications import notifications_bp
    # --- 新增导入 ---
    from .api.dashboard import dashboard_bp
    from .api.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')

    # 引入模型，以便Flask-Migrate可以检测到
    # --- CHANGED: 引入所有模型文件 ---
    from .models import user, order, commission, notification

    return app