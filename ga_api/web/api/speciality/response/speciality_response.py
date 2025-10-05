from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SpecialityResponse(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)
