import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from ga_api.db.models.users import User, current_active_user
from ga_api.services.professional_service import ProfessionalService
from ga_api.web.api.professionals.request.professional_create_request import (
    ProfessionalCreateRequest,
)
from ga_api.web.api.professionals.request.professional_update_request import (
    ProfessionalUpdateRequest,
)
from ga_api.web.api.professionals.response.professional_create_response import (
    ProfessionalResponse,
)

router = APIRouter()
admin_router = APIRouter()


@admin_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProfessionalResponse,
)
async def create_professional(
    professional_create: ProfessionalCreateRequest,
    admin_user: Annotated[User, Depends(current_active_user)],
    service: ProfessionalService = Depends(),
) -> ProfessionalResponse:
    return await service.create_professional(  # type: ignore
        professional_create,
        admin_user,
    )


@admin_router.put("/{professional_id}", response_model=ProfessionalResponse)
async def update_professional(
    professional_id: uuid.UUID,
    professional_update: ProfessionalUpdateRequest,
    admin_user: Annotated[User, Depends(current_active_user)],
    service: ProfessionalService = Depends(),
) -> ProfessionalResponse:
    return await service.update_professional(  # type: ignore
        professional_id,
        professional_update,
        admin_user,
    )


@admin_router.get("/", response_model=List[ProfessionalResponse])
async def get_all_professionals(
    admin_user: Annotated[User, Depends(current_active_user)],
    service: ProfessionalService = Depends(),
    limit: int | None = 50,
    offset: int | None = 0,
) -> List[ProfessionalResponse]:
    return await service.get_all_professionals_admin(admin_user, limit, offset)  # type: ignore


@router.get("/", response_model=List[ProfessionalResponse])
async def get_all_professionals_public(
    current_user: Annotated[User, Depends(current_active_user)],
    service: ProfessionalService = Depends(),
    limit: int | None = 50,
    offset: int | None = 0,
) -> List[ProfessionalResponse]:
    return await service.get_all_professionals(limit, offset)  # type: ignore
