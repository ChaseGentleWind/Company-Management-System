# backend/app/models/notification.py

from .. import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, comment="通知ID(主键)")
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment="接收通知的用户ID")
    content = db.Column(db.String(255), nullable=False, comment="通知内容")
    is_read = db.Column(db.Boolean, default=False, nullable=False, comment="是否已读")
    
    # 可选，用于点击通知后跳转到相关订单
    related_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True, comment="(可选)关联的订单ID,用于跳转") # [cite: 128]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="通知创建时间")

    # 关系定义
    recipient = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id} for User {self.recipient_id}>'