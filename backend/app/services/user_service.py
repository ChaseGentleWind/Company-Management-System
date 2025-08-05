# backend/app/services/user_service.py

import bcrypt
from .. import db
from ..models.user import User, UserRole
from ..schemas import user_schemas

def get_user_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()

def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)

def get_all_users() -> list[User]:
    return User.query.order_by(User.id).all()

def get_active_developers() -> list[User]:
    """获取所有已启用的技术人员列表"""
    return User.query.filter_by(role=UserRole.DEVELOPER, is_active=True).order_by(User.id).all()

def create_user(user_data: user_schemas.UserCreate) -> User:
    """创建新用户"""
    if get_user_by_username(user_data.username):
        raise ValueError("Username already exists")

    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hashed_password.decode('utf-8'),
        role=user_data.role,
        gender=user_data.gender,
        skills=user_data.skills,
        default_commission_rate=user_data.default_commission_rate,
        financial_account=user_data.financial_account
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user(user_id: int, update_data: user_schemas.UserUpdate) -> User:
    """更新用户信息"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    if 'username' in update_dict and update_dict['username'] != user.username:
        if get_user_by_username(update_dict['username']):
            raise ValueError("Username already exists")

    for key, value in update_dict.items():
        if key == 'password':
            if value: # 确保密码非空
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(user, 'password_hash', hashed_password.decode('utf-8'))
        else:
            setattr(user, key, value)
            
    db.session.commit()
    return user

def toggle_user_status(user_id: int) -> User:
    """启用/禁用用户"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    
    user.is_active = not user.is_active
    db.session.commit()
    return user

def delete_user(user_id: int):
    """删除用户"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    db.session.delete(user)
    db.session.commit()