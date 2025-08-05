# backend/app/services/order_service.py

from .. import db
from ..models.user import User, UserRole
from ..models.order import Order, OrderStatus
from ..schemas import order_schemas
from datetime import datetime
import random

# --- ADDED: 导入通知服务 ---
from . import notification_service 
from . import commission_service # <-- 新增导入

def generate_order_uid():
    """生成格式为 PREFIX-YYYYMMDD-XXXX 的唯一订单ID"""
    prefix = "PROJ"
    date_str = datetime.utcnow().strftime('%Y%m%d')
    random_part = f'{random.randint(0, 9999):04d}'
    # 在实际生产中，还需要检查ID是否已存在，如果存在则重新生成
    return f"{prefix}-{date_str}-{random_part}"

def create_order(order_data: order_schemas.OrderCreate, creator_id: int) -> Order:
    """
    创建新订单并存入数据库
    """
    new_order = Order(
        order_uid=generate_order_uid(),
        customer_info=order_data.customer_info,
        requirements_desc=order_data.requirements_desc,
        creator_id=creator_id
    )
    db.session.add(new_order)
    db.session.commit()
    return new_order

def get_orders_for_user(user_id: int, user_role: str):
    """
    根据用户角色获取其有权查看的订单列表
    """
    query = Order.query.order_by(Order.created_at.desc())
    
    if user_role == UserRole.SUPER_ADMIN.value or user_role == UserRole.FINANCE.value:
        return query.all()
    elif user_role == UserRole.CUSTOMER_SERVICE.value:
        return query.filter_by(creator_id=user_id).all()
    elif user_role == UserRole.DEVELOPER.value:
        return query.filter_by(developer_id=user_id).all()
    
    return [] # 其他角色或无角色，返回空列表

# --- ADDED: 订单状态流转的核心逻辑 ---
# 定义状态机: { '当前角色': { '当前状态': ['允许的目标状态1', '允许的目标状态2'] } }
# 定义状态机 (保持不变)
VALID_TRANSITIONS = {
    UserRole.CUSTOMER_SERVICE.value: {
        OrderStatus.PENDING_ASSIGNMENT: [OrderStatus.PENDING_PAYMENT, OrderStatus.CANCELLED],
        OrderStatus.PENDING_PAYMENT: [OrderStatus.IN_DEVELOPMENT, OrderStatus.CANCELLED],
        OrderStatus.IN_DEVELOPMENT: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.RECEIVED, OrderStatus.IN_DEVELOPMENT, OrderStatus.CANCELLED],
        OrderStatus.RECEIVED: [OrderStatus.IN_DEVELOPMENT, OrderStatus.CANCELLED],
    },
    UserRole.DEVELOPER.value: {
        OrderStatus.RECEIVED: [OrderStatus.PENDING_SETTLEMENT]
    },
    UserRole.FINANCE.value: {
        OrderStatus.PENDING_SETTLEMENT: [OrderStatus.VERIFIED], # 审核通过，触发提成计算
        OrderStatus.VERIFIED: [OrderStatus.SETTLED] # 确认结算，锁定订单
    },
    UserRole.SUPER_ADMIN.value: {
        # 超管可以取消任何未锁定状态的订单 (简化处理，赋予更大权限)
        OrderStatus.PENDING_ASSIGNMENT: [OrderStatus.CANCELLED],
        OrderStatus.PENDING_PAYMENT: [OrderStatus.CANCELLED],
        OrderStatus.IN_DEVELOPMENT: [OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.CANCELLED],
        OrderStatus.RECEIVED: [OrderStatus.CANCELLED],
        OrderStatus.PENDING_SETTLEMENT: [OrderStatus.CANCELLED],
    }
}

def get_order_by_id(order_id: int) -> Order | None:
    """通过ID获取订单"""
    return db.session.get(Order, order_id)

def update_order_status(order: Order, target_status: OrderStatus, user_role: str) -> Order:
    """更新订单状态，内置权限和逻辑校验"""
    # 【修复点】检查订单是否锁定
    if order.is_locked:
        raise ValueError("Order is locked and cannot be modified.")

    current_status = order.status
    
    # ... (权限和状态转换校验逻辑保持不变) ...
    role_transitions = VALID_TRANSITIONS.get(user_role)
    if not role_transitions:
        raise PermissionError("You do not have permission to change order status.")

    allowed_statuses = role_transitions.get(current_status)
    if not allowed_statuses or target_status not in allowed_statuses:
        raise ValueError(f"Transition from {current_status.value} to {target_status.value} is not allowed for your role.")

    # 更新状态和相关时间戳
    order.status = target_status
    if target_status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.utcnow()
    
    # --- 触发通知和业务逻辑 ---
    if target_status == OrderStatus.PENDING_SETTLEMENT and order.developer:
        content = f"订单 [{order.order_uid}] 已被技术人员 {order.developer.full_name} 确认为可结算，请审核。"
        notification_service.notify_all_finances(content, order.id)

    # 【Bug 2 修复】当财务核验通过时，计算提成
    if target_status == OrderStatus.VERIFIED:
        commission_service.calculate_and_create_commissions(order)
        # 可以选择性地通知客服和技术提成已生成
        if order.creator:
             notification_service.create_notification(order.creator.id, f"您的订单 [{order.order_uid}] 提成已计算完成。", order.id)
        if order.developer:
             notification_service.create_notification(order.developer.id, f"您的订单 [{order.order_uid}] 提成已计算完成。", order.id)
            
    # 【Bug 1 修复】当订单最终完成或取消时，锁定订单
    if target_status in [OrderStatus.SETTLED, OrderStatus.CANCELLED]:
        order.is_locked = True
        
    db.session.commit()
    return order


def update_order_details_by_cs(order: Order, update_data: order_schemas.OrderUpdateByCs) -> Order:
    """由客服更新订单信息（价格、分配技术）"""
    if order.is_locked:
        raise ValueError("Order is locked and cannot be modified.")
    
    update_dict = update_data.model_dump(exclude_unset=True)

    if 'final_price' in update_dict:
        order.final_price = update_dict['final_price']

    if 'developer_id' in update_dict and update_dict['developer_id'] != order.developer_id:
        developer_id = update_dict['developer_id']
        # 这里可以增加一个判断，如果传入的 developer_id 是 null，则表示取消分配
        if developer_id:
            developer = db.session.get(User, developer_id)
            if not developer or developer.role != UserRole.DEVELOPER:
                raise ValueError("Invalid developer ID or user is not a developer.")
            
            order.developer_id = developer_id
            # ---【任务4.2】新增通知逻辑 ---
            content = f"您有一个新订单 [{order.order_uid}] 被分配给您，请及时跟进。"
            notification_service.create_notification(developer.id, content, order.id)
        else:
            # 如果传入的 developer_id 为空，则视为取消分配
            order.developer_id = None


    db.session.commit()
    return order


def set_commission_override(order: Order, override_data: order_schemas.CommissionOverrideUpdate) -> Order:
    """由超管设置特殊提成"""
    if order.is_locked:
        raise ValueError("Order is locked and cannot be modified.")
        
    current_override = order.commission_rate_override or {}
    update_dict = override_data.model_dump(exclude_unset=True)
    
    current_override.update(update_dict)
    order.commission_rate_override = current_override
    
    db.session.commit()
    return order