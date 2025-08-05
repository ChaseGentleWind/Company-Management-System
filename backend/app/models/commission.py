# backend/app/models/commission.py

from .. import db
from datetime import datetime

class Commission(db.Model):
    __tablename__ = 'commissions'

    id = db.Column(db.Integer, primary_key=True, comment="提成记录ID(主键)")
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment="关联的订单ID")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment="提成归属的用户ID")
    
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment="提成金额") # [cite: 122]
    
    # 记录计算时该用户在订单中的角色，防止未来用户角色变动导致数据不清
    role_at_time = db.Column(db.String(50), nullable=False, comment="计算时该用户在订单中的角色(客服/技术)") # [cite: 122]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="提成计算时间")
    
    # 关系定义
    order = db.relationship('Order', back_populates='commissions')
    user = db.relationship('User', back_populates='commissions')

    def __repr__(self):
        return f'<Commission {self.id} for Order {self.order_id}>'