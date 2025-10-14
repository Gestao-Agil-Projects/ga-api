from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.users import (
    UserCreate,
    UserManager,
    UserRead,
    UserUpdate,
    api_users,
    auth_jwt,
    get_user_manager,
)
from ga_api.services.mail_service import MailService
from ga_api.services.user_service import UserService
from ga_api.web.api.users.request.user_patient_request import UserPatientRequest


async def get_user_service(
    mail_service: MailService = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
    user_dao: UserDAO = Depends(UserDAO),
) -> UserService:
    return UserService(mail_service, user_manager, user_dao)


router = APIRouter()
admin_router = APIRouter()

router.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
router.include_router(
    api_users.get_auth_router(auth_jwt),
    prefix="/auth/jwt",
    tags=["auth"],
)


@admin_router.post(
    "/register-patient",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: UserPatientRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    user = await service.register_patient_user(request)
    return UserRead.model_validate(user)
