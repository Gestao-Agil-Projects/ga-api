import uuid

from pydantic import BaseModel


class SpecialityDto(BaseModel):
    id: uuid.UUID
    title: str
