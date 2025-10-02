import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ProfessionalUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
