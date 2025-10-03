from typing import Any

from fastapi import APIRouter, Depends

from ga_api.db.models.users import User
from ga_api.services.scheduling_service import SchedulingService
from ga_api.web.api.admin.dependencies import get_current_admin_user
from ga_api.web.api.admin.request.adm_scheduling_request import BookForPatientRequest
from ga_api.web.api.admin.response.adm_scheduling_response import SchedulingResponse

admin_router = APIRouter()


@admin_router.post("/schedule/schedule-for-patient", response_model=SchedulingResponse)
async def book_for_patient(
    request: BookForPatientRequest,
    admin: User = Depends(get_current_admin_user),
    scheduling_service: SchedulingService = Depends(),
) -> Any:
    return await scheduling_service.schedule_for_patient_by_admin(
        availability_id=request.availability_id,
        patient_email=request.patient_email,
        admin_user=admin,
    )
