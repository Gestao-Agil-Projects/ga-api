from typing import Annotated, List

from fastapi import APIRouter, Depends

from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.users import User, UserRead, current_active_user
from ga_api.enums.user_role import UserRole
from ga_api.utils.admin_utils import AdminUtils

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
