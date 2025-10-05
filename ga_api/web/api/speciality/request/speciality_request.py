from pydantic import BaseModel, field_validator


class SpecialityRequest(BaseModel):

    title: str

    @field_validator("title")
    def title_not_empty(cls, v: str) -> str:  # noqa: N805
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v
