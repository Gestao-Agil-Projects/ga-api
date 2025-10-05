import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from ga_api.dto.speciality_dto import SpecialityDTO


class ProfessionalResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    bio: Optional[str] = None
    specialities: Optional[List[SpecialityDTO]] = []

    model_config = ConfigDict(from_attributes=True)
