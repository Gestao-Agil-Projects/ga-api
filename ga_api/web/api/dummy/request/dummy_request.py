from pydantic import BaseModel


class DummyRequest(BaseModel):
    """DTO for creating new dummy model."""

    name: str
