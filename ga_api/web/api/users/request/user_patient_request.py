from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

from ga_api.enums.consultation_frequency import ConsultationFrequency


class UserPatientRequest(BaseModel):
    email: EmailStr
    cpf: str
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    full_name: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    frequency: ConsultationFrequency = ConsultationFrequency.AS_NEEDED
