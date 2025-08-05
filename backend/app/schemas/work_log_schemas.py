# backend/app/schemas/work_log_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .user_schemas import UserOut # 用于嵌套显示用户信息

# 用于在订单详情中显示的技术人员简要信息
class UserInLogOut(BaseModel):
    id: int
    full_name: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class WorkLogBase(BaseModel):
    log_content: str

# ---【任务4.1】新增用于创建的 Schema ---
class WorkLogCreate(WorkLogBase):
    log_content: str = Field(..., min_length=1, description="日志内容不能为空")

class WorkLogOut(WorkLogBase):
    id: int
    created_at: datetime
    user_id: int
    developer: UserInLogOut

    model_config = ConfigDict(from_attributes=True)