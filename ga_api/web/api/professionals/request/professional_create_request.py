import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict



class ProfessionalCreateRequest(BaseModel):
    full_name: str
    bio: Optional[str] = None
    phone: Optional[str] = None
    email: str
    is_enabled: bool = True
    specialities: List[uuid.UUID | None] = []



