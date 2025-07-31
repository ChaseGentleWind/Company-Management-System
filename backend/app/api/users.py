from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import bcrypt

from .. import db
from ..models.user import User, UserRole
from ..schemas import user_schemas
from ..utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt # 确保 get_jwt 已导入

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('SUPER_ADMIN')
def create_user_route():
    """创建新用户"""
    try:
        user_data = user_schemas.UserCreate.model_validate(request.get_json())
        
        if User.query.filter_by(username=user_data.username).first():
            return jsonify({"msg": "Username already exists"}), 409

        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(
            username=user_data.username,
            full_name=user_data.full_name,
            password_hash=hashed_password.decode('utf-8'),
            role=user_data.role,
            gender=user_data.gender,
            specialized_field=user_data.specialized_field,
            default_commission_rate=user_data.default_commission_rate,
            financial_account=user_data.financial_account
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # FIX: Add mode='json' to correctly serialize the Enum
        return jsonify(user_schemas.UserOut.model_validate(new_user).model_dump(mode='json')), 201
    
    except ValidationError as e:
        return jsonify(e.errors()), 400

@users_bp.route('/', methods=['GET'])
@jwt_required()
# 移除 @role_required('SUPER_ADMIN') 装饰器，因为我们将在这里处理逻辑
def get_users_route():
    """获取用户列表（根据调用者角色返回不同数据）"""
    
    # 从JWT中获取当前用户的角色
    claims = get_jwt()
    current_user_role = claims.get("role")

    query = User.query

    if current_user_role == UserRole.SUPER_ADMIN.value:
        # 如果是超管，返回所有用户
        users = query.order_by(User.id).all()
    elif current_user_role == UserRole.CUSTOMER_SERVICE.value:
        # 如果是客服，只返回所有“已启用”的技术人员列表
        users = query.filter_by(role=UserRole.DEVELOPER, is_active=True).order_by(User.id).all()
    else:
        # 对于其他角色（如技术、财务），他们无权获取用户列表，返回空
        users = []

    users_out = [user_schemas.UserOut.model_validate(user).model_dump(mode='json') for user in users]
    return jsonify(users_out), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('SUPER_ADMIN')
def get_user_route(user_id: int):
    """获取单个用户信息"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # FIX: Add mode='json'
    return jsonify(user_schemas.UserOut.model_validate(user).model_dump(mode='json')), 200

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('SUPER_ADMIN')
def update_user_route(user_id: int):
    """更新用户信息"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    try:
        update_data = user_schemas.UserUpdate.model_validate(request.get_json())
        update_dict = update_data.model_dump(exclude_unset=True)

        if 'username' in update_dict and update_dict['username'] != user.username:
            if User.query.filter_by(username=update_dict['username']).first():
                return jsonify({"msg": "Username already exists"}), 409

        for key, value in update_dict.items():
            if key == 'password':
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(user, 'password_hash', hashed_password.decode('utf-8'))
            else:
                setattr(user, key, value)
        
        db.session.commit()
        
        # FIX: Add mode='json'
        return jsonify(user_schemas.UserOut.model_validate(user).model_dump(mode='json')), 200
    
    except ValidationError as e:
        return jsonify(e.errors()), 400

@users_bp.route('/<int:user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@role_required('SUPER_ADMIN')
def toggle_user_status_route(user_id: int):
    """启用/禁用用户"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.is_active = not user.is_active
    db.session.commit()
    
    # FIX: Add mode='json'
    return jsonify(user_schemas.UserOut.model_validate(user).model_dump(mode='json')), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('SUPER_ADMIN')
def delete_user_route(user_id: int):
    """删除用户"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    
    return '', 204