# backend/app/models/order.py

from datetime import datetime
from enum import Enum
from .. import db
from sqlalchemy.dialects.mysql import JSON

# 订单状态的枚举 (保持不变, 与文档流程吻合)
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

# 订单数据模型
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    
    # --- ADDED: 业务ID，根据需求文档添加 ---
    order_uid = db.Column(db.String(50), unique=True, nullable=False, comment="业务ID, PREFIX-YYYYMMDD-XXXX") # 

    # --- CHANGED: 修改为JSON类型以存储结构化客户信息 ---
    customer_info = db.Column(JSON, nullable=False, comment="客户信息, 如{\"name\": \"张三\", \"phone\": ...}") # 

    requirements_desc = db.Column(db.Text, nullable=False, comment="需求描述")
    
    # --- CHANGED: 修改为Numeric以确保财务计算精度 ---
    final_price = db.Column(db.Numeric(10, 2), nullable=True, comment="订单价格") # 
    
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING_ASSIGNMENT)

    # 外键关联
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # 创建人 (客服)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # 负责人 (技术)

    # --- ADDED: 用于存储特殊提成比例 ---
    commission_rate_override = db.Column(JSON, nullable=True, comment="特殊提成比例, 如 {\"cs_rate\": 12.5, \"tech_rate\": 15.0}") # 

    # --- ADDED: 订单锁定标记 ---
    is_locked = db.Column(db.Boolean, default=False, nullable=False, comment="订单是否锁定(已结算/已取消)") # 

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime, nullable=True)

    # 关系定义
    creator = db.relationship('User', back_populates='orders_created', foreign_keys=[creator_id])
    developer = db.relationship('User', back_populates='orders_assigned', foreign_keys=[developer_id])
    logs = db.relationship('WorkLog', back_populates='order', cascade="all, delete-orphan")
    
    # --- ADDED: 新增与提成表的关系 ---
    commissions = db.relationship('Commission', back_populates='order', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id}>'

# 工作日志模型 (保持不变, 但为清晰起见，移除budget等无关字段，并调整外键关系)
class WorkLog(db.Model):
    __tablename__ = 'work_logs'

    id = db.Column(db.Integer, primary_key=True)
    log_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # 使用 created_at 更通用

    # 外键关联
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    # --- CHANGED: 字段名与需求文档对齐 ---
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment="填写日志的技术人员ID") # [cite: 125]

    # 关系定义
    order = db.relationship('Order', back_populates='logs')
    developer = db.relationship('User', back_populates='work_logs')

    def __repr__(self):
        return f'<WorkLog for Order {self.order_id}>'