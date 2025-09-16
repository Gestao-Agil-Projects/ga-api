from typing import List

from ga_api.db.dao.dummy_dao import DummyDAO
from ga_api.db.models.dummy_model import DummyModel
from ga_api.web.api.dummy.request.dummy_request import DummyRequest
from ga_api.web.api.dummy.response.dummy_response import DummyResponse


class DummyService:
    def __init__(self, dummy_dao: DummyDAO) -> None:
        self.dummy_dao = dummy_dao

    async def create_dummy(self, request: DummyRequest) -> DummyResponse:
        dummy = DummyModel(
            name=request.name,
        )

        return await self.dummy_dao.save(dummy)  # type: ignore

    async def get_dummy_models(self, limit: int, offset: int) -> List[DummyResponse]:
        return await self.dummy_dao.get_all_dummies(limit, offset)  # type: ignore
