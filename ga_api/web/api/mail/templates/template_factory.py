# ruff: noqa

from fastapi_mail import MessageSchema

from ga_api.web.api.mail.request.mail_request import MailRequest

# TODO: alterar na versão final
CALM_MIND_URL = "https://viewer-alpha-68223955.figma.site/"


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

    @staticmethod
    def create_first_access_password_template(
        request: MailRequest, password: str
    ) -> MessageSchema:
        html = f"""
        <html>
        <body style="margin:0;padding:0;background:#f0ece6;font-family:Arial,sans-serif;color:#2d2d2d;font-size:14px;">
            <div style="max-width:520px;margin:30px auto;background:#fff;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.08);overflow:hidden;">
                <div style="background:#4a90e2;padding:20px;text-align:center;color:#fff;">
                    <h2 style="margin:0;font-weight:600;">Calm Mind</h2>
                </div>
                <div style="padding:25px;">
                    <p style="margin:0 0 10px;">Olá, <strong>{request.email}</strong>! 😊</p>
                    <p style="margin:0 0 15px;">Bem-vindo(a) à plataforma <strong>Calm Mind</strong>!</p>
                    <p style="margin:0 0 15px;">Para realizar seu <strong>primeiro acesso</strong>, utilize a senha gerada abaixo:</p>

                    <div style="background:#f3f3f5;border:1px solid #0000001a;padding:12px;border-radius:8px;text-align:center;font-size:18px;letter-spacing:1px;font-weight:bold;color:#2d2d2d;margin:10px 0 20px;">
                        {password}
                    </div>

                    <p style="margin:0 0 25px;">Por segurança, <strong>não compartilhe</strong> esta senha com ninguém.</p>

                    <div style="text-align:center;">
                        <a href="{CALM_MIND_URL}"
                           style="background:#4a90e2;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:500;display:inline-block;">
                            Acessar Plataforma
                        </a>
                    </div>

                    <hr style="margin:30px 0;border:none;border-top:1px solid #ececf0;">

                    <p style="font-size:12px;color:#717182;text-align:center;margin:0;">
                        © 2025 Calm Mind. Todos os direitos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return MessageSchema(
            subject="Calm Mind | Primeiro Acesso",
            recipients=[request.email],
            body=html,
            subtype="html",  # type: ignore
        )
