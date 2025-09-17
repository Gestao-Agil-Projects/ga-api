from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.dummy_model import DummyModel


class DummyDAO(AbstractDAO[DummyModel]):
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=DummyModel, session=session)

    async def filter(self, name: Optional[str] = None) -> List[DummyModel]:
        """
        Get specific dummy model.

        :param name: name of dummy instance.
        :return: dummy models.
        """
        query = select(DummyModel)
        if name:
            query = query.where(DummyModel.name == name)
        rows = await self._session.execute(query)
        return list(rows.scalars().fetchall())

    async def find_by_name(self, dummy_name: str) -> DummyModel | None:
        result = await self._session.execute(
            select(DummyModel).where(DummyModel.name == dummy_name),
        )
        return result.scalar_one_or_none()
