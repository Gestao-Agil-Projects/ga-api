from pydantic import BaseModel, EmailStr


class ScheduleRequest(BaseModel):
    patient_email: EmailStr
