# backend/app/schemas/notification_schemas.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    content: str
    is_read: bool
    related_order_id: Optional[int] = None
    created_at: datetime

class NotificationOut(NotificationBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)