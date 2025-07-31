# backend/app/models/order.py

from datetime import datetime
from enum import Enum
from .. import db

# 1. 定义订单状态的枚举
# 这比直接使用字符串更规范，可防止拼写错误，也便于前端使用
class OrderStatus(Enum):
    PENDING_ASSIGNMENT = '待匹配'
    PENDING_PAYMENT = '待付款'
    IN_DEVELOPMENT = '开发中'
    SHIPPED = '已发货'
    RECEIVED = '已收货'
    PENDING_SETTLEMENT = '可结算'
    VERIFIED = '已核验'
    SETTLED = '已结算'
    CANCELLED = '已取消'

# 2. 定义订单数据模型
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_info = db.Column(db.String(500), nullable=False) # 客户信息
    requirements_desc = db.Column(db.Text, nullable=False) # 需求描述
    initial_budget = db.Column(db.Float, nullable=True) # 初始预算
    final_price = db.Column(db.Float, nullable=True) # 最终成交价格
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING_ASSIGNMENT) # 订单状态

    # 外键关联
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # 创建人 (客服)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # 负责人 (技术)

    # 特殊提成比例
    special_commission_rate = db.Column(db.Float, nullable=True)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime, nullable=True) # 发货时间

    # 关系定义
    creator = db.relationship('User', back_populates='orders_created', foreign_keys=[creator_id])
    developer = db.relationship('User', back_populates='orders_assigned', foreign_keys=[developer_id])
    logs = db.relationship('WorkLog', back_populates='order', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'

# 3. 定义工作日志模型
class WorkLog(db.Model):
    __tablename__ = 'work_logs'

    id = db.Column(db.Integer, primary_key=True)
    log_content = db.Column(db.Text, nullable=False) # 日志内容
    log_date = db.Column(db.Date, nullable=False, default=datetime.utcnow) # 日志日期

    # 外键关联
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 关系定义
    order = db.relationship('Order', back_populates='logs')
    developer = db.relationship('User', back_populates='work_logs')

    def __repr__(self):
        return f'<WorkLog for Order {self.order_id}>'