from typing import Annotated, Any

from fastapi import APIRouter
from fastapi.param_functions import Depends

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.models.users import current_active_user
from ga_api.services.availability_service import AvailabilityService
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest
from ga_api.web.api.availability.response.availability_response import (
    AvailabilityResponse,
)

admin_router = APIRouter()


def get_availability_service(
    availability_dao: Annotated[AvailabilityDAO, Depends()],
) -> AvailabilityService:
    return AvailabilityService(availability_dao)


@admin_router.post("/", response_model=AvailabilityResponse)
async def register_availability(
    request: AvailabilityRequest,
    user: Annotated[Any, Depends(current_active_user)],
    availability_service: Annotated[
        AvailabilityService,
        Depends(get_availability_service),
    ],
) -> AvailabilityResponse:
    return await availability_service.register_availability(request, user)  # type: ignore
