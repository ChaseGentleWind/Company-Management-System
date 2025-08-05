# backend/app/services/work_log_service.py (新建文件)

from .. import db
from ..models.order import Order, WorkLog
from ..models.user import UserRole
from ..schemas import work_log_schemas

def add_work_log(order: Order, user_id: int, user_role: str, log_data: work_log_schemas.WorkLogCreate) -> WorkLog:
    """
    为订单添加一条新的工作日志。
    执行权限和逻辑校验。
    """
    # 校验1: 只有技术人员可以填写日志
    if user_role != UserRole.DEVELOPER.value:
        raise PermissionError("Only developers can add work logs.")

    # 校验2: 填写日志的技术必须是该订单的负责人
    if order.developer_id != user_id:
        raise PermissionError("You are not the developer assigned to this order.")

    # 校验3: 已锁定的订单不能添加日志
    if order.is_locked:
        raise ValueError("Cannot add work log to a locked order.")

    new_log = WorkLog(
        order_id=order.id,
        user_id=user_id,
        log_content=log_data.log_content
    )

    db.session.add(new_log)
    db.session.commit()

    return new_log