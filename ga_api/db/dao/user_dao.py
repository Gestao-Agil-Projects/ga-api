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


    from typing import List
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.users import User
from ga_api.enums.user_role import UserRole


class UserDAO(AbstractDAO[User]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(User, session)

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email),  # type: ignore
        )
        return result.scalar_one_or_none()
        
    async def get_all_by_role(
        self, role: UserRole, skip: int = 0, limit: int = 100
    ) -> List[User]:
        result = await self._session.execute(
            select(self._AbstractDAO__model)  # type: ignore
            .where(self._AbstractDAO__model.role == role)  # type: ignore
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
