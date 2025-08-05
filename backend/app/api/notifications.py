# backend/app/api/notifications.py (新建文件)

from flask import Blueprint, jsonify
from pydantic import ValidationError
from ..services import notification_service
from ..schemas import notification_schemas
from flask_jwt_extended import jwt_required, get_jwt_identity

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_notifications():
    """获取当前登录用户的通知列表"""
    try:
        current_user_id = int(get_jwt_identity())
        notifications = notification_service.get_notifications_for_user(current_user_id)
        
        # 使用 Pydantic Schema 进行序列化
        notifications_out = [
            notification_schemas.NotificationOut.model_validate(n).model_dump(mode='json') 
            for n in notifications
        ]
        return jsonify(notifications_out), 200
        
    except Exception as e:
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id: int):
    """将单条通知标记为已读"""
    try:
        current_user_id = int(get_jwt_identity())
        updated_notification = notification_service.mark_notification_as_read(
            notification_id,
            current_user_id
        )
        
        if not updated_notification:
            return jsonify({"msg": "Notification not found or access denied"}), 404
            
        return jsonify(
            notification_schemas.NotificationOut.model_validate(updated_notification).model_dump(mode='json')
        ), 200

    except PermissionError as e:
         return jsonify({"msg": str(e)}), 403
    except Exception as e:
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500