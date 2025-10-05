from uuid import UUID

from pydantic import BaseModel, EmailStr


class AdminScheduleRequest(BaseModel):
    availability_id: UUID
    email: EmailStr
