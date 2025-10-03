from typing import Optional

from pydantic import BaseModel


class ProfessionalUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
