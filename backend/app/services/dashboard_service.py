# backend/app/services/dashboard_service.py

from sqlalchemy import func
from datetime import datetime, timedelta
from .. import db
from ..models.user import User, UserRole
from ..models.order import Order, OrderStatus
from ..models.commission import Commission

def get_personal_stats(user_id: int, user_role: str):
    """为客服/技术提供个人业绩统计"""
    
    # 获取本月时间范围
    today = datetime.utcnow()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    stats = {}

    if user_role == UserRole.CUSTOMER_SERVICE.value:
        # 本月创建订单数
        monthly_orders = db.session.query(func.count(Order.id)).filter(
            Order.creator_id == user_id,
            Order.created_at >= start_of_month
        ).scalar()

        # 累计总提成
        total_commission = db.session.query(func.sum(Commission.amount)).filter(
            Commission.user_id == user_id,
            Commission.role_at_time == UserRole.CUSTOMER_SERVICE.value
        ).scalar()
        
        stats = {
            "monthly_orders_created": monthly_orders or 0,
            "total_commission_earned": float(total_commission or 0)
        }

    elif user_role == UserRole.DEVELOPER.value:
        # 本月完成订单数 (状态变为 '可结算' 或更高)
        monthly_completed = db.session.query(func.count(Order.id)).filter(
            Order.developer_id == user_id,
            Order.status.in_([
                OrderStatus.PENDING_SETTLEMENT, 
                OrderStatus.VERIFIED, 
                OrderStatus.SETTLED
            ]),
            Order.updated_at >= start_of_month
        ).scalar()

        # 累计总提成
        total_commission = db.session.query(func.sum(Commission.amount)).filter(
            Commission.user_id == user_id,
            Commission.role_at_time == UserRole.DEVELOPER.value
        ).scalar()
        
        stats = {
            "monthly_orders_completed": monthly_completed or 0,
            "total_commission_earned": float(total_commission or 0)
        }
        
    return stats

def get_global_stats():
    """为超管提供全局数据看板"""
    
    total_users = db.session.query(func.count(User.id)).scalar()
    total_orders = db.session.query(func.count(Order.id)).scalar()
    
    # 统计所有已结算订单的总金额
    total_settled_value = db.session.query(func.sum(Order.final_price)).filter(
        Order.status == OrderStatus.SETTLED
    ).scalar()

    # 按状态统计订单数量
    orders_by_status = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()

    # 格式化为字典
    status_distribution = {status.value: count for status, count in orders_by_status}

    return {
        "total_users": total_users or 0,
        "total_orders": total_orders or 0,
        "total_settled_value": float(total_settled_value or 0),
        "status_distribution": status_distribution
    }