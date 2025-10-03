from uuid import UUID

from pydantic import BaseModel


class PatientScheduleRequest(BaseModel):
    availability_id: UUID
