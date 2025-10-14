from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.dependencies import get_db_session
from ga_api.web.api.availability.response.availability_response import AvailabilityResponse
from ga_api.db.models.users import User, current_active_user
from ga_api.services.schedule_service import SchedulingService
from ga_api.web.api.schedule.request.admin_schedule_request import AdminScheduleRequest
from ga_api.web.api.schedule.request.patient_schedule_request import (
    PatientScheduleRequest,
)
from ga_api.web.api.schedule.response.schedule_response import SchedulingResponse

router = APIRouter()
admin_router = APIRouter()


@router.post("/", response_model=SchedulingResponse)
async def book_appointment(
    request: PatientScheduleRequest,
    patient: User = Depends(current_active_user),
    scheduling_service: SchedulingService = Depends(),
) -> Any:
    return await scheduling_service.schedule_patient(request, patient)


@admin_router.post("/", response_model=SchedulingResponse)
async def book_for_patient(
    request: AdminScheduleRequest,
    admin: User = Depends(current_active_user),
    scheduling_service: SchedulingService = Depends(),
) -> Any:
    return await scheduling_service.schedule_for_patient_by_admin(
        request,
        admin,
    )


@router.get("/", response_model=List[AvailabilityResponse])
async def get_my_schedules(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    dao = AvailabilityDAO(session)
    availabilities = await dao.find_by_patient_id(user.id)
    return [AvailabilityResponse.model_validate(a) for a in availabilities]
