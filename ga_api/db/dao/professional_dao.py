# ga_api/db/dao/professional_dao.py

import uuid
from typing import List, Optional

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

    async def get_all_with_specialities(self) -> List[Professional]:
        query = select(Professional).options(selectinload(Professional.specialities))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def find_by_id_with_specialities(
        self,
        professional_id: uuid.UUID,
    ) -> Optional[Professional]:
        """
        Encontra um profissional pelo ID com as suas especialidades pré-carregadas.
        """
        query = (
            select(Professional)
            .where(Professional.id == professional_id)
            .options(selectinload(Professional.specialities))
        )
        result = await self._session.execute(query)
        return result.scalars().one_or_none()
