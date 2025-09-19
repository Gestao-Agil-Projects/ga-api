from fastapi_mail import ConnectionConfig

from ga_api.settings import settings


class MailConfiguration:

    def __init__(self) -> None:
        self.conf = ConnectionConfig(  # type: ignore
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,  # type: ignore
            MAIL_FROM=settings.mail_username,  # type: ignore
            MAIL_PORT=settings.mail_port,  # type: ignore
            MAIL_SERVER=settings.mail_server,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
