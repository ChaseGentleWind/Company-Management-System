# backend/app/schemas/commission_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal

class CommissionBase(BaseModel):
    user_id: int
    amount: Decimal
    role_at_time: str

class CommissionOut(CommissionBase):
    id: int
    created_at: datetime
    
    # --- ADDED: 嵌套返回用户信息，便于前端展示 ---
    full_name: str | None = Field(None, alias="user.full_name")

    model_config = ConfigDict(from_attributes=True)