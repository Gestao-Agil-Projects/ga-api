import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from ga_api.web.api.professionals.dto.specialty_dto import SpecialityDto


class ProfessionalResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    bio: Optional[str] = None
    specialities: List[SpecialityDto]

    model_config = ConfigDict(from_attributes=True)
