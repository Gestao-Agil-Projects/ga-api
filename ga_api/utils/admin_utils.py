from typing import Any

from starlette import status
from starlette.exceptions import HTTPException

from ga_api.db.models.users import User


class AdminUtils:

    @staticmethod
    def validate_user_is_admin(user: User) -> None:
        if not user.is_superuser:
            raise HTTPException(
                detail="User does not have admin privileges",
                status_code=status.HTTP_403_FORBIDDEN,
            )

    @staticmethod
    def populate_admin_data(obj: Any, admin: User, update_only: bool = False) -> None:
        if not admin.is_superuser:
            raise Exception("This action can only be performed by superusers")

        if not update_only and hasattr(obj, "created_by_admin_id"):
            obj.created_by_admin_id = admin.id

        if hasattr(obj, "updated_by_admin_id"):
            obj.updated_by_admin_id = admin.id
