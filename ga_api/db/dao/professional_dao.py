# ga_api/db/dao/professional_dao.py

from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.professionals_model import Professional


class ProfessionalDAO(AbstractDAO[Professional]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(Professional, session)

    async def find_all_with_specialities(
        self,
        limit: int = 50,
        offset: int = 0,
        only_enabled: bool = False,
    ) -> List[Professional]:
        """
        Find all professionals by id with their specialities loaded.
        """
        query = (
            select(Professional)
            .options(selectinload(Professional.specialities))
            .limit(limit)
            .offset(offset)
        )

        if only_enabled:
            query.where(Professional.is_enabled)

        result = await self._session.execute(query)
        return list(result.scalars().all())
