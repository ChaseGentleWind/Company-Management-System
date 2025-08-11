# backend/app/schemas/order_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from ..models.order import OrderStatus
from .user_schemas import UserOut
# --- ADDED: 导入新创建的schemas ---
from .work_log_schemas import WorkLogOut
from .commission_schemas import CommissionOut

# 用于在订单信息中精简显示的用户模型
class UserInOrderOut(BaseModel):
    id: int
    full_name: Optional[str] = None
    financial_account: Optional[str] = None # + 新增此字段
    model_config = ConfigDict(from_attributes=True)

# --- CHANGED: 创建订单时，只接收最基本信息 ---
class OrderCreate(BaseModel):
    customer_info: Dict[str, Any] = Field(..., description="客户信息, e.g. {'name': '张三', 'phone': '138...'}")
    requirements_desc: str = Field(..., min_length=1)

# --- ADDED: 局部更新订单时，客服可提交的数据 ---
class OrderUpdateByCs(BaseModel):
    final_price: Optional[Decimal] = Field(None, ge=0, description="订单价格")
    developer_id: Optional[int] = Field(None, description="分配的技术人员ID")

# --- ADDED: 局部更新订单状态的Schema ---
class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., description="目标状态")

# --- ADDED: 超管设置特殊提成的Schema ---
class CommissionOverrideUpdate(BaseModel):
    cs_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    tech_rate: Optional[Decimal] = Field(None, ge=0, le=100)

# --- CHANGED: 从API返回订单信息的标准格式，包含所有关联信息 ---
class OrderOut(BaseModel):
    id: int
    order_uid: str
    customer_info: Dict[str, Any]
    requirements_desc: str
    final_price: Optional[Decimal] = None
    status: OrderStatus
    
    creator: UserInOrderOut
    developer: Optional[UserInOrderOut] = None
    
    commission_rate_override: Optional[Dict[str, float]] = None
    is_locked: bool

    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    
    # --- ADDED: 嵌套返回工作日志和提成信息 ---
    logs: List[WorkLogOut] = []
    commissions: List[CommissionOut] = []

    model_config = ConfigDict(from_attributes=True)