from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    user_id: int
    username: Optional[str] = "User"