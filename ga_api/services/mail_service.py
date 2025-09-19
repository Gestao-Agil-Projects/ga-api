from secrets import randbelow

from fastapi_mail import FastMail, MessageSchema

from ga_api.web.api.mail.configuration.mail_configuration import MailConfiguration
from ga_api.web.api.mail.request.mail_request import MailRequest
from ga_api.web.api.mail.templates.template_factory import TemplateFactory


def generate_random_token() -> str:
    return f"{randbelow(1000000):06}"


class MailService:
    def __init__(self) -> None:
        self.mail_config: MailConfiguration = MailConfiguration()
        self.fm: FastMail = FastMail(self.mail_config.conf)

    async def send_email_reset_password(self, request: MailRequest) -> None:
        template_message: MessageSchema = (
            TemplateFactory.create_reset_password_template(
                request,
                generate_random_token(),
            )
        )
        await self.fm.send_message(template_message)
