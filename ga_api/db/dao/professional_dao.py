# ga_api/db/dao/professional_dao.py
from datetime import datetime, timedelta
from typing import List

from fastapi import Depends
from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.block_model import Block
from ga_api.db.models.professionals_model import Professional


class ProfessionalDAO(AbstractDAO[Professional]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(Professional, session)

    async def find_all_with_specialities(
        self,
        limit: int = 50,
        offset: int = 0,
        only_enabled: bool = False,
    ) -> List[tuple[Professional, bool]]:
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
        end_of_day = start_of_day + timedelta(days=1)

        is_blocked_subq = (
            exists().where(
                and_(
                    Block.professional_id == Professional.id,
                    Block.start_time < end_of_day,
                    Block.end_time > start_of_day,
                ),
            )
        ).label("is_blocked")

        query = (
            select(Professional, is_blocked_subq)
            .options(selectinload(Professional.specialities))
            .limit(limit)
            .offset(offset)
        )

        if only_enabled:
            query = query.where(Professional.is_enabled.is_(True))

        result = await self._session.execute(query)
        return result.all()  # type: ignore
