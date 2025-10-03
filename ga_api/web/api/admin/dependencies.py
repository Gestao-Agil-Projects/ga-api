from fastapi import Depends, HTTPException

from ga_api.db.models.users import User, current_active_user


async def get_current_admin_user(
    current_user: User = Depends(current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return current_user
