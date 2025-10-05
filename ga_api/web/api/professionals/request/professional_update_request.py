from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ProfessionalUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_enabled: Optional[bool] = None
    specialities: Optional[List[UUID]] = None
