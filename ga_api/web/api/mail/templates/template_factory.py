from fastapi_mail import MessageSchema

from ga_api.web.api.mail.request.mail_request import MailRequest


class TemplateFactory:

    @staticmethod
    def create_reset_password_template(
        request: MailRequest,
        token: str,
    ) -> MessageSchema:
        return MessageSchema(
            subject="Calm Mind | Recuperação de Senha",
            recipients=[request.email],
            body=f"Olá! O código para recuperar a senha é {token}",
            subtype="plain",  # type: ignore
        )
