from pydantic import BaseModel, ConfigDict


class DummyResponse(BaseModel):
    """
    DTO for dummy models.

    It returned when accessing dummy models from the API.
    """

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
