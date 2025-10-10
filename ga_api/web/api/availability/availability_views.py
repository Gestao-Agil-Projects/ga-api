from typing import Annotated, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi.param_functions import Depends

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.dao.professional_dao import ProfessionalDAO
from ga_api.db.models.users import current_active_user
from ga_api.services.availability_service import AvailabilityService
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest
from ga_api.web.api.availability.request.update_availability_request import (
    UpdateAvailabilityRequest,
)
from ga_api.web.api.availability.response.availability_response import (
    AvailabilityResponse,
)

admin_router = APIRouter()
router = APIRouter()


def get_availability_service(
    availability_dao: Annotated[AvailabilityDAO, Depends()],
    professional_dao: Annotated[ProfessionalDAO, Depends()],
) -> AvailabilityService:
    return AvailabilityService(availability_dao, professional_dao)


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


@admin_router.put("/{availability_id}", response_model=AvailabilityResponse)
async def update_availability(
    availability_id: UUID,
    request: UpdateAvailabilityRequest,
    user: Annotated[Any, Depends(current_active_user)],
    availability_service: Annotated[
        AvailabilityService,
        Depends(get_availability_service),
    ],
) -> AvailabilityResponse:
    return await availability_service.update_availability(  # type: ignore
        availability_id,
        request,
        user,
    )


@admin_router.get("/")
async def get_availability_admin(
    availability_service: Annotated[
        AvailabilityService,
        Depends(get_availability_service),
    ],
    professional_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[AvailabilityResponse]:

    return await availability_service.get_availabilities_admin(  # type: ignore
        professional_id,
        limit,
        offset,
    )


@router.get("/")
async def get_availability_patient(
    user: Annotated[Any, Depends(current_active_user)],
    availability_service: Annotated[
        AvailabilityService,
        Depends(get_availability_service),
    ],
    professional_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[AvailabilityResponse]:

    return await availability_service.get_availabilities_patient(  # type: ignore
        professional_id,
        limit,
        offset,
    )
