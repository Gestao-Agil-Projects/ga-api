from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.block_model import Block


class BlockDAO(AbstractDAO[Block]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Block, session=session)

    async def find_all_by_professional_id(self, professional_id: UUID) -> List[Block]:
        if not professional_id:
            return []

        result = await self._session.execute(
            select(Block).where(Block.professional_id == professional_id),
        )
        return result.scalars().all()  # type: ignore
