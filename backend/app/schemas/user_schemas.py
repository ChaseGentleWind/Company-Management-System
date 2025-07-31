from pydantic import BaseModel, Field
from typing import Optional
from ..models.user import UserRole

# 基础模式，包含所有角色共有的字段
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole
    gender: Optional[str] = Field(None, max_length=10)
    specialized_field: Optional[str] = Field(None, max_length=255)
    default_commission_rate: Optional[float] = Field(None, ge=0, le=1)
    financial_account: Optional[str] = Field(None, max_length=255)
    
    # Pydantic V2 配置
    class Config:
        from_attributes = True

# 创建用户时使用的模式，需要提供密码
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# 更新用户时使用的模式，所有字段都是可选的
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    gender: Optional[str] = Field(None, max_length=10)
    specialized_field: Optional[str] = Field(None, max_length=255)
    default_commission_rate: Optional[float] = Field(None, ge=0, le=1)
    financial_account: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)

# 从API返回用户信息时使用的模式，不包含密码哈希
class UserOut(UserBase):
    id: int
    is_active: bool