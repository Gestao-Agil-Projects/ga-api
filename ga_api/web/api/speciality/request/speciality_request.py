from pydantic import BaseModel


class SpecialityRequest(BaseModel):
    """DTO for creating new dummy model."""

    title: str
