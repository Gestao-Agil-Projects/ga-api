from typing import Annotated, Any

from fastapi.params import Depends
from starlette import status
from starlette.exceptions import HTTPException

from ga_api.db.models.users import current_active_user


async def admin_required(user: Annotated[Any, Depends(current_active_user)]) -> None:
    if not user.is_superuser:
        raise HTTPException(
            detail="User does not have admin privileges",
            status_code=status.HTTP_403_FORBIDDEN,
        )
