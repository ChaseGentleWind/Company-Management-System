# backend/app/services/dashboard_service.py

from sqlalchemy import func, extract
from datetime import datetime
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

def get_team_performance_stats() -> dict:
    """
    获取团队绩效统计（本月）
    :return: 包含客服和技术团队业绩的字典
    """
    today = datetime.utcnow()
    current_month = today.month
    current_year = today.year

    # 1. 查询客服团队业绩（按本月创建订单的金额排名）
    cs_performance = db.session.query(
        User.full_name,
        func.sum(Order.final_price).label('total_amount')
    ).join(
        Order, User.id == Order.creator_id
    ).filter(
        User.role == UserRole.CUSTOMER_SERVICE,
        extract('year', Order.created_at) == current_year,
        extract('month', Order.created_at) == current_month,
        Order.final_price.isnot(None) # 只统计已定价的订单
    ).group_by(
        User.id
    ).order_by(
        func.sum(Order.final_price).desc()
    ).all()

    # 2. 查询技术团队业绩（按本月完成结算的订单金额排名）
    dev_performance = db.session.query(
        User.full_name,
        func.sum(Order.final_price).label('total_amount')
    ).join(
        Order, User.id == Order.developer_id
    ).filter(
        User.role == UserRole.DEVELOPER,
        # 订单的最终更新时间（变为SETTLED状态的时间）在本月
        extract('year', Order.updated_at) == current_year,
        extract('month', Order.updated_at) == current_month,
        Order.status == OrderStatus.SETTLED # 只统计已结算的订单
    ).group_by(
        User.id
    ).order_by(
        func.sum(Order.final_price).desc()
    ).all()

    # 格式化结果
    formatted_cs = [{"full_name": name, "total_value": float(amount or 0)} for name, amount in cs_performance]
    formatted_dev = [{"full_name": name, "total_value": float(amount or 0)} for name, amount in dev_performance]

    return {
        "customer_service_performance": formatted_cs,
        "developer_performance": formatted_dev
    }