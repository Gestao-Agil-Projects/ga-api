from fastapi_mail.errors import ConnectionErrors
from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.users import User, UserCreate, UserManager
from ga_api.services.mail_service import MailService
from ga_api.utils.token_utils import TokenUtils
from ga_api.web.api.mail.request.mail_request import MailRequest
from ga_api.web.api.users.request.user_patient_request import UserPatientRequest


class UserService:
    def __init__(
        self,
        mail_service: MailService,
        user_manager: UserManager,
        user_dao: UserDAO,
    ) -> None:
        self.mail_service = mail_service
        self.user_manager = user_manager
        self.user_dao = user_dao

    async def register_patient_user(self, request: UserPatientRequest) -> User:
        if await self.user_dao.find_by_email(request.email):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists.",
            )

        random_password = TokenUtils.generate_random_password()
        user_create = UserCreate(
            **request.model_dump(),
            password=random_password,
            is_first_access=True,
        )
        mail_request = MailRequest(email=request.email)

        try:
            await self.mail_service.send_email_first_access(
                mail_request,
                random_password,
            )

        except ConnectionErrors as e:
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not connect to the email server. Try again later.",
            ) from e

        return await self.user_manager.create(user_create, safe=True)
