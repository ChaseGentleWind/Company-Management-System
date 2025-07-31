from .. import db
from enum import Enum
import bcrypt

# 定义用户角色的枚举
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
    # --- 其他字段保持不变 ---
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.DEVELOPER)
    gender = db.Column(db.String(10), nullable=True)
    specialized_field = db.Column(db.String(255), nullable=True)
    default_commission_rate = db.Column(db.Float, nullable=True)
    financial_account = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # --- 新增关系 ---
    # 一个客服创建多个订单
    orders_created = db.relationship('Order', back_populates='creator', foreign_keys='Order.creator_id', lazy='dynamic')
    # 一个技术负责多个订单
    orders_assigned = db.relationship('Order', back_populates='developer', foreign_keys='Order.developer_id', lazy='dynamic')
    # 一个技术有多个工作日志
    work_logs = db.relationship('WorkLog', back_populates='developer', lazy='dynamic')


    def __repr__(self):
        return f'<User {self.username}>'
