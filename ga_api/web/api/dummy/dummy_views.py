from typing import Annotated, Any, List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from ga_api.db.dao.dummy_dao import DummyDAO
from ga_api.db.models.users import current_active_user
from ga_api.services.dummy_service import DummyService
from ga_api.web.api.dummy.request.dummy_request import DummyRequest
from ga_api.web.api.dummy.response.dummy_response import DummyResponse

router = APIRouter()


def get_dummy_service(dummy_dao: Annotated[DummyDAO, Depends()]) -> DummyService:
    return DummyService(dummy_dao)


@router.get("/", response_model=List[DummyResponse])
async def get_dummy_models(
    user: Annotated[Any, Depends(current_active_user)],
    dummy_service: Annotated[DummyService, Depends(get_dummy_service)],
    dummy_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
) -> List[DummyResponse]:

    return await dummy_service.get_dummy_models(limit, offset, dummy_id)  # type: ignore


@router.put("/", status_code=204)
async def create_dummy_model(
    request: DummyRequest,
    dummy_service: Annotated[DummyService, Depends(get_dummy_service)],
) -> None:

    await dummy_service.create_dummy(request)


@router.delete("/", status_code=204)
async def delete_dummy_model(
    user: Annotated[Any, Depends(current_active_user)],
    dummy_service: Annotated[DummyService, Depends(get_dummy_service)],
    dummy_id: int | None = None,
    dummy_name: str | None = None,
) -> None:
    await dummy_service.delete_dummy(dummy_id, dummy_name)


@router.patch("/")
async def update_dummy_model(
    user: Annotated[Any, Depends(current_active_user)],
    dummy_id: int,
    request: DummyRequest,
    dummy_service: Annotated[DummyService, Depends(get_dummy_service)],
) -> DummyResponse:

    return await dummy_service.update_dummy(dummy_id, request)  # type: ignore
