# backend/app/services/notification_service.py

from .. import db
from ..models.notification import Notification
from ..models.user import User, UserRole

def create_notification(recipient_id: int, content: str, related_order_id: int = None):
    """
    创建一个新的通知并存入数据库
    """
    notification = Notification(
        recipient_id=recipient_id,
        content=content,
        related_order_id=related_order_id
    )
    db.session.add(notification)
    # 此处的 commit 将由调用它的上层业务函数统一处理

def notify_all_finances(content: str, related_order_id: int):
    """
    通知所有财务人员
    """
    finance_users = User.query.filter_by(role=UserRole.FINANCE, is_active=True).all()
    for user in finance_users:
        create_notification(user.id, content, related_order_id)
        
def get_notifications_for_user(user_id: int) -> list[Notification]:
    """
    获取指定用户的所有通知，按时间倒序排列。
    """
    return Notification.query.filter_by(recipient_id=user_id).order_by(Notification.created_at.desc()).all()


def mark_notification_as_read(notification_id: int, user_id: int) -> Notification | None:
    """
    将指定ID的通知标记为已读。
    同时校验操作者是否为通知的接收者。
    """
    notification = db.session.get(Notification, notification_id)
    
    # 校验通知是否存在
    if not notification:
        return None
        
    # 校验操作权限
    if notification.recipient_id != user_id:
        raise PermissionError("You do not have permission to modify this notification.")
        
    notification.is_read = True
    db.session.commit()
    
    return notification