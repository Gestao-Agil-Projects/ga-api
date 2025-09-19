from fastapi import APIRouter, Depends

from ga_api.services.mail_service import MailService
from ga_api.web.api.mail.request.mail_request import MailRequest


def get_mail_service() -> MailService:
    return MailService()


router = APIRouter()


@router.post("/email", status_code=204)
async def send_email_reset_password(
    request: MailRequest,
    service: MailService = Depends(get_mail_service),
) -> None:

    return await service.send_email_reset_password(request)
