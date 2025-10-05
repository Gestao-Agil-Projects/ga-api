from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.users import User


class UserDAO(AbstractDAO[User]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(User, session)

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email),  # type: ignore
        )
        return result.scalar_one_or_none()
