from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from ga_api.db.dao.dummy_dao import DummyDAO
from ga_api.db.models.dummy_model import DummyModel
from ga_api.web.api.dummy.request.dummy_request import DummyRequest


class DummyService:
    def __init__(self, dummy_dao: DummyDAO) -> None:
        self.dummy_dao = dummy_dao

    async def create_dummy(self, request: DummyRequest) -> None:
        dummy = DummyModel(**request.model_dump(exclude_unset=True))
        await self.dummy_dao.save(dummy)

    async def get_dummy_models(
        self,
        limit: int,
        offset: int,
        dummy_id: UUID | None,
    ) -> List[DummyModel]:
        if not dummy_id:
            return await self.dummy_dao.find_all(limit, offset)

        dummy: Optional[DummyModel] = await self.dummy_dao.find_by_id(dummy_id)

        return [dummy] if dummy else []

    async def delete_dummy(self, dummy_id: int | None, dummy_name: str | None) -> None:
        if dummy_id:
            await self.dummy_dao.delete_by_id(dummy_id)
            return

        if dummy_name:
            dummy_by_name = await self.dummy_dao.find_by_name(dummy_name)
            if dummy_by_name:
                await self.dummy_dao.delete(dummy_by_name)

    async def update_dummy(self, dummy_id: int, request: DummyRequest) -> DummyModel:
        dummy: Optional[DummyModel] = await self.dummy_dao.find_by_id(dummy_id)

        if not dummy:
            raise HTTPException(
                detail="Dummy not found",
                status_code=404,
            )

        return await self.dummy_dao.update(dummy, request.model_dump())
