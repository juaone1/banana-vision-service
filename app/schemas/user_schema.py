from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class UserOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class PaginatedUsers(BaseModel):
    users: List[UserOut]
    total: int
    error: Optional[Any] = None
