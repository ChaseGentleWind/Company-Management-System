# backend/app/models/user.py

from .. import db
from enum import Enum
from sqlalchemy.dialects.mysql import JSON # 建议显式导入

# 定义用户角色的枚举 (保持不变)
class UserRole(Enum):
    SUPER_ADMIN = 'SUPER_ADMIN'
    CUSTOMER_SERVICE = 'CUSTOMER_SERVICE'
    DEVELOPER = 'DEVELOPER'
    FINANCE = 'FINANCE'

# 用户数据模型
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.DEVELOPER)
    gender = db.Column(db.String(10), nullable=True)
    
    # --- CHANGED: 字段重命名并修改类型以支持JSON格式的技能标签 ---
    skills = db.Column(JSON, nullable=True, comment="擅长领域(为技术角色)") # 

    # --- CHANGED: 修改为Numeric以确保财务计算精度 ---
    default_commission_rate = db.Column(db.Numeric(5, 2), nullable=True, comment="默认提成比例,如10.00(%)") # 

    financial_account = db.Column(db.String(255), nullable=True, comment="财务账号(银行卡/支付宝)") # 
    is_active = db.Column(db.Boolean, default=True)

    # --- 关系定义 (保持不变) ---
    # 一个客服创建多个订单
    orders_created = db.relationship('Order', back_populates='creator', foreign_keys='Order.creator_id', lazy='dynamic')
    # 一个技术负责多个订单
    orders_assigned = db.relationship('Order', back_populates='developer', foreign_keys='Order.developer_id', lazy='dynamic')
    # 一个技术有多个工作日志
    work_logs = db.relationship('WorkLog', back_populates='developer', lazy='dynamic')

    # --- ADDED: 新增与提成和通知表的关系 ---
    commissions = db.relationship('Commission', back_populates='user', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='recipient', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'