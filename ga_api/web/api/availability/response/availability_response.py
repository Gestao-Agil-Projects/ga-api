from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ga_api.enums.availability_status import AvailabilityStatus


class AvailabilityResponse(BaseModel):
    id: UUID
    status: AvailabilityStatus
    start_time: datetime
    end_time: datetime
    professional_id: UUID
    patient_id: Optional[UUID] = None

    class Config:
        from_attributes = True
