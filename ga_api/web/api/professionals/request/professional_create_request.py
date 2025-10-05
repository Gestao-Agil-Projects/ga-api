import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ProfessionalCreateRequest(BaseModel):
    full_name: str
    bio: Optional[str] = None
    phone: str
    email: EmailStr
    is_enabled: bool = True
    specialities: Optional[List[uuid.UUID]] = []
