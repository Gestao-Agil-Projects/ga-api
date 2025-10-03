from uuid import UUID

from pydantic import BaseModel


class BookAppointmentRequest(BaseModel):
    availability_id: UUID
