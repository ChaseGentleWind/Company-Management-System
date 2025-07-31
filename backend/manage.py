import click
import bcrypt  # <-- 1. 导入 bcrypt 库
from flask.cli import with_appcontext
from app import create_app, db
from app.models.user import User, UserRole

# 创建 Flask app 实例以获取应用上下文
app = create_app()

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """创建一个新的超级管理员账户"""
    with app.app_context():
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            print(f"Error: Username '{username}' already exists.")
            return

        # 2. 在此显式地哈希密码
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        )

        # 3. 创建用户实例时直接传入哈希后的密码
        admin_user = User(
            username=username,
            full_name="Super Admin",
            password_hash=hashed_password.decode('utf-8'), # 传入哈希值
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        
        # admin_user.set_password(password)  <-- 4. 这行旧代码已被替换

        # 存入数据库
        db.session.add(admin_user)
        db.session.commit()
        print(f"Successfully created SUPER_ADMIN user: '{username}'.")