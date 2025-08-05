# backend/app/api/users.py

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from .. import db
from ..models.user import UserRole
from ..schemas import user_schemas
from ..utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt

# --- ADDED: 导入新的服务层 ---
from ..services import user_service

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def create_user_route():
    """创建新用户"""
    try:
        user_data = user_schemas.UserCreate.model_validate(request.get_json())
        
        # --- CHANGED: 调用服务层 ---
        new_user = user_service.create_user(user_data)
        
        return jsonify(user_schemas.UserOut.model_validate(new_user).model_dump(mode='json')), 201
    
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409 # 409 Conflict for existing username
    except Exception as e:
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users_route():
    """获取用户列表（根据调用者角色返回不同数据）"""
    claims = get_jwt()
    current_user_role = claims.get("role")

    # --- CHANGED: 业务逻辑移至服务层 ---
    if current_user_role == UserRole.SUPER_ADMIN.value:
        users = user_service.get_all_users()
    elif current_user_role == UserRole.CUSTOMER_SERVICE.value:
        users = user_service.get_active_developers()
    else:
        users = [] # 其他角色无权获取列表

    users_out = [user_schemas.UserOut.model_validate(user).model_dump(mode='json') for user in users]
    return jsonify(users_out), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def get_user_route(user_id: int):
    """获取单个用户信息"""
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify(user_schemas.UserOut.model_validate(user).model_dump(mode='json')), 200

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def update_user_route(user_id: int):
    """更新用户信息"""
    try:
        update_data = user_schemas.UserUpdate.model_validate(request.get_json())
        
        # --- CHANGED: 调用服务层 ---
        updated_user = user_service.update_user(user_id, update_data)
        
        return jsonify(user_schemas.UserOut.model_validate(updated_user).model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e:
        # 根据错误信息判断是404还是409
        if "not found" in str(e).lower():
            return jsonify({"msg": str(e)}), 404
        else:
            return jsonify({"msg": str(e)}), 409
    except Exception as e:
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500


@users_bp.route('/<int:user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def toggle_user_status_route(user_id: int):
    """启用/禁用用户"""
    try:
        # --- CHANGED: 调用服务层 ---
        updated_user = user_service.toggle_user_status(user_id)
        return jsonify(user_schemas.UserOut.model_validate(updated_user).model_dump(mode='json')), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def delete_user_route(user_id: int):
    """删除用户"""
    try:
        # --- CHANGED: 调用服务层 ---
        user_service.delete_user(user_id)
        return '', 204
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404