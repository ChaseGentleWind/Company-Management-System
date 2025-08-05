# backend/app/api/dashboard.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..services import dashboard_service
from ..models.user import UserRole
from ..utils.decorators import role_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/personal', methods=['GET'])
@jwt_required()
def get_personal_dashboard():
    """获取个人业绩仪表盘数据 (客服/技术)"""
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get("role")

    if user_role not in [UserRole.CUSTOMER_SERVICE.value, UserRole.DEVELOPER.value]:
        return jsonify({"msg": "This endpoint is for Customer Service or Developers only"}), 403

    stats = dashboard_service.get_personal_stats(current_user_id, user_role)
    return jsonify(stats), 200

@dashboard_bp.route('/global', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def get_global_dashboard():
    """获取全局数据看板 (仅限超管)"""
    stats = dashboard_service.get_global_stats()
    return jsonify(stats), 200