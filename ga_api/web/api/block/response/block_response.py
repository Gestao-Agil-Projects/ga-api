from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BlockResponse(BaseModel):
    id: UUID
    professional_id: UUID
    start_time: datetime
    end_time: datetime
    reason: str

    model_config = ConfigDict(from_attributes=True)
