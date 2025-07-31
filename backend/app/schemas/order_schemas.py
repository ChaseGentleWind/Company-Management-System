# backend/app/schemas/order_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from ..models.order import OrderStatus
from .user_schemas import UserOut # 导入UserOut以嵌套显示用户信息

# 用于在订单信息中精简显示的用户模型
class UserInOrderOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    # --- 新增下面这行配置 ---
    model_config = ConfigDict(from_attributes=True)

# 创建订单时，客服需要提交的数据
class OrderCreate(BaseModel):
    customer_info: str = Field(..., min_length=1, max_length=500)
    requirements_desc: str = Field(..., min_length=1)
    initial_budget: Optional[float] = Field(None, ge=0)
    final_price: Optional[float] = Field(None, ge=0)
    developer_id: Optional[int] = None # 创建时即可分配技术

# 更新订单时，允许修改的字段
class OrderUpdate(BaseModel):
    customer_info: Optional[str] = Field(None, min_length=1, max_length=500)
    requirements_desc: Optional[str] = Field(None, min_length=1)
    initial_budget: Optional[float] = Field(None, ge=0)
    final_price: Optional[float] = Field(None, ge=0)
    developer_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    special_commission_rate: Optional[float] = Field(None, ge=0, le=1)

# 从API返回订单信息的标准格式
class OrderOut(BaseModel):
    id: int
    customer_info: str
    requirements_desc: str
    initial_budget: Optional[float] = None
    final_price: Optional[float] = None
    status: OrderStatus
    creator_id: int
    developer_id: Optional[int] = None
    special_commission_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None

    # 嵌套显示创建者和负责人的简要信息
    creator: UserInOrderOut
    developer: Optional[UserInOrderOut] = None

    # Pydantic v2 需要使用 ConfigDict
    model_config = ConfigDict(from_attributes=True)