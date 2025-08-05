# backend/app/services/commission_service.py (新增文件)

from decimal import Decimal
from .. import db
from ..models.order import Order
from ..models.commission import Commission
from ..models.user import User, UserRole

def calculate_and_create_commissions(order: Order):
    """
    为已核验的订单计算并创建提成记录。
    这是一个核心业务逻辑。
    """
    if not order.final_price or order.final_price <= 0:
        print(f"订单 {order.id} 价格无效，跳过提成计算。")
        return

    # 清除旧的提成记录，以防重复计算
    Commission.query.filter_by(order_id=order.id).delete()

    # 准备提成计算所需的数据
    final_price = order.final_price
    override_rates = order.commission_rate_override or {}

    # 1. 计算客服的提成
    if order.creator and order.creator.role == UserRole.CUSTOMER_SERVICE:
        cs_rate = override_rates.get('cs_rate')
        if cs_rate is None and order.creator.default_commission_rate is not None:
            cs_rate = order.creator.default_commission_rate
        
        if cs_rate is not None:
            amount = final_price * (Decimal(str(cs_rate)) / 100)
            commission_cs = Commission(
                order_id=order.id,
                user_id=order.creator_id,
                amount=amount,
                role_at_time=UserRole.CUSTOMER_SERVICE.value
            )
            db.session.add(commission_cs)
            print(f"为客服 {order.creator.full_name} 计算提成: {amount}")

    # 2. 计算技术人员的提成
    if order.developer and order.developer.role == UserRole.DEVELOPER:
        tech_rate = override_rates.get('tech_rate')
        if tech_rate is None and order.developer.default_commission_rate is not None:
            tech_rate = order.developer.default_commission_rate

        if tech_rate is not None:
            amount = final_price * (Decimal(str(tech_rate)) / 100)
            commission_tech = Commission(
                order_id=order.id,
                user_id=order.developer_id,
                amount=amount,
                role_at_time=UserRole.DEVELOPER.value
            )
            db.session.add(commission_tech)
            print(f"为技术 {order.developer.full_name} 计算提成: {amount}")

    # 注意：这里的 commit 将由上层调用者 (update_order_status) 统一执行