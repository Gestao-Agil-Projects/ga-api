from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.speciality_model import Speciality


class SpecialityDAO(AbstractDAO[Speciality]):
    """Class for accessing the specialities table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Speciality, session=session)

    async def get_by_title(self, title: str) -> Optional[Speciality]:
        """
        Get a specific speciality model by its title.

        :param title: The title of the speciality.
        :return: A single Speciality model if found, otherwise None.
        """
        query = select(Speciality).where(Speciality.title == title)
        result = await self._session.execute(query)
        return result.scalars().first()
