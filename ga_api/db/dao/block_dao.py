from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.block_model import Block


class BlockDAO(AbstractDAO[Block]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Block, session=session)
