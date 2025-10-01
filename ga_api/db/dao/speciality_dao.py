from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.speciality_model import Speciality


class SpecialityDAO(AbstractDAO[Speciality]):
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Speciality, session=session)

    async def filter(self, name: Optional[str] = None) -> List[Speciality]:
        """
        Get specific dummy model.

        :param name: name of dummy instance.
        :return: dummy models.
        """
        query = select(Speciality)
        if name:
            query = query.where(Speciality.name == name)
        rows = await self._session.execute(query)
        return list(rows.scalars().fetchall())

    async def find_by_name(self, speciality_name: str) -> Speciality | None:
        result = await self._session.execute(
            select(Speciality).where(Speciality.name == speciality_name),
        )
        return result.scalar_one_or_none()
