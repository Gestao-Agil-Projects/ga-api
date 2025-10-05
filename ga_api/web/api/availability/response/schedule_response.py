from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ga_api.enums.availability_status import AvailabilityStatus


class SchedulingResponse(BaseModel):
    id: UUID
    start_time: datetime
    end_time: datetime
    status: AvailabilityStatus
    professional_id: UUID
    patient_id: Optional[UUID] = None

    class Config:
        from_attributes = True
