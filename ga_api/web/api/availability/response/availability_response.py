from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AvailabilityResponse(BaseModel):

    id: UUID
    start_time: datetime
    end_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
