from pydantic import BaseModel, EmailStr


class MailRequest(BaseModel):
    email: EmailStr
