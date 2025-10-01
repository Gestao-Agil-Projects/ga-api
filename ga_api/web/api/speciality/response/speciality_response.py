from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SpecialityResponse(BaseModel):
    """
    DTO for dummy models.

    It returned when accessing dummy models from the API.
    """

    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)
