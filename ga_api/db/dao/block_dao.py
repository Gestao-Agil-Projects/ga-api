from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.block_model import BlockModel


class BlockDAO(AbstractDAO[BlockModel]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=BlockModel, session=session)

    async def save_block(self, block: BlockModel) -> BlockModel:
        self._session.add(block)
        await self._session.flush()
        await self._session.refresh(block)
        return block

    async def remove_block_by_id(self, block_id: int) -> None:
        await self._session.execute(delete(BlockModel).where(BlockModel.id == block_id))
        await self._session.flush()
