from fastapi import APIRouter, Depends

from ga_api.db.models.users import (
    UserCreate,
    UserRead,
    UserUpdate,
    api_users,
    auth_jwt,
)
from typing import Annotated, List


from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.users import User, UserRead, current_active_user
from ga_api.enums.user_role import UserRole
from ga_api.utils.admin_utils import AdminUtils

router = APIRouter()

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

router = APIRouter()


@router.get("/patients", response_model=List[UserRead])
async def get_all_patients(
    admin_user: Annotated[User, Depends(current_active_user)],
    user_dao: UserDAO = Depends(),
    skip: int = 0,
    limit: int = 100,
) -> List[UserRead]:

    AdminUtils.validate_user_is_admin(admin_user)
    return await user_dao.get_all_by_role(role=UserRole.PATIENT, skip=skip, limit=limit)
