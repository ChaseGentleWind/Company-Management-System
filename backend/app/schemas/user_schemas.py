# backend/app/schemas/user_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal
from ..models.user import UserRole

# 基础模式，包含所有角色共有的字段
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole
    gender: Optional[str] = Field(None, max_length=10)
    
    # --- CHANGED: 字段名和类型与模型对齐 ---
    skills: Optional[List[str]] = Field(None, description="技术人员的技能标签, 如 ['Java', 'UI设计']")
    
    # --- CHANGED: 类型与模型对齐 ---
    default_commission_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="默认提成比例, 10.50 表示 10.50%")
    
    financial_account: Optional[str] = Field(None, max_length=255)
    
    # Pydantic V2 配置
    model_config = ConfigDict(from_attributes=True)

# 创建用户时使用的模式，需要提供密码
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# 更新用户时使用的模式，所有字段都是可选的
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    gender: Optional[str] = Field(None, max_length=10)
    skills: Optional[List[str]] = Field(None)
    default_commission_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    financial_account: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None

# 从API返回用户信息时使用的模式，不包含密码哈希
class UserOut(UserBase):
    id: int
    is_active: bool