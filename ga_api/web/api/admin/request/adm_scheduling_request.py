from uuid import UUID

from pydantic import BaseModel, EmailStr


class BookForPatientRequest(BaseModel):
    availability_id: UUID
    patient_email: EmailStr
