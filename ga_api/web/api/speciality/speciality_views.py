import uuid
from typing import Annotated, Any, List

from fastapi import APIRouter
from fastapi.param_functions import Depends

from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.models.users import current_active_user
from ga_api.services.speciality_service import SpecialityService
from ga_api.web.api.speciality.request.speciality_request import SpecialityRequest
from ga_api.web.api.speciality.response.speciality_response import SpecialityResponse

admin_router = APIRouter()


def get_speciality_service(
    speciality_dao: Annotated[SpecialityDAO, Depends()],
) -> SpecialityService:
    return SpecialityService(speciality_dao)


@admin_router.get("/", response_model=List[SpecialityResponse])
async def get_speciality_models(
    user: Annotated[Any, Depends(current_active_user)],
    speciality_service: Annotated[SpecialityService, Depends(get_speciality_service)],
    speciality_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
) -> List[SpecialityResponse]:

    return await speciality_service.get_speciality_models(limit, offset, speciality_id)  # type: ignore


@admin_router.put("/", status_code=204)
async def update_speciality_model(
    user: Annotated[Any, Depends(current_active_user)],
    speciality_id: uuid.UUID,
    request: SpecialityRequest,
    speciality_service: Annotated[SpecialityService, Depends(get_speciality_service)],
) -> None:

    await speciality_service.update_speciality(user, speciality_id, request)


@admin_router.post("/", status_code=204)
async def create_speciality(
    user: Annotated[Any, Depends(current_active_user)],
    request: SpecialityRequest,
    speciality_service: Annotated[SpecialityService, Depends(get_speciality_service)],
) -> None:

    await speciality_service.create_speciality(user, request)


@admin_router.delete("/", status_code=204)
async def delete_speciality_model(
    user: Annotated[Any, Depends(current_active_user)],
    speciality_service: Annotated[SpecialityService, Depends(get_speciality_service)],
    speciality_id: uuid.UUID,
) -> None:
    await speciality_service.delete_speciality(speciality_id)
