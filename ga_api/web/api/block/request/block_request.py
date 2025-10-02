from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator


class BlockCreateRequest(BaseModel):
    professional_id: UUID
    start_time: datetime
    end_time: datetime
    reason: str

    @model_validator(mode="after")
    def validate_time_order(self) -> "BlockCreateRequest":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be after end_time")
        return self
