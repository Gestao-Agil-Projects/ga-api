from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AvailabilityRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    professional_id: UUID
