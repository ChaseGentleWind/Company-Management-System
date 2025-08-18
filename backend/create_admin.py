from app import create_app, db
from app.models.user import User, UserRole
import bcrypt

app = create_app()
with app.app_context():
    try:
        # 检查admin用户是否已存在
        existing_user = User.query.filter_by(username='admin').first()
        if existing_user:
            print('Admin user already exists')
        else:
            # 创建管理员用户
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                username='admin',
                password_hash=hashed_password.decode('utf-8'),
                role=UserRole.SUPER_ADMIN
            )
            db.session.add(admin_user)
            db.session.commit()
            print('Admin user created successfully')
    except Exception as e:
        print('Error:', e)
        import traceback
        traceback.print_exc()
