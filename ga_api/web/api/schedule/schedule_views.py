from typing import Any

from fastapi import APIRouter, Depends

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
