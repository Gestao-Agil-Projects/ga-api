from typing import Any

from fastapi import APIRouter, Depends

from ga_api.db.models.users import User, current_active_user
from ga_api.services.scheduling_service import SchedulingService
from ga_api.web.api.scheduling.request.scheduling_request import BookAppointmentRequest
from ga_api.web.api.scheduling.response.scheduling_response import SchedulingResponse

scheduling_router = APIRouter()


@scheduling_router.post("/schedule", response_model=SchedulingResponse)
async def book_appointment(
    request: BookAppointmentRequest,
    patient: User = Depends(current_active_user),
    scheduling_service: SchedulingService = Depends(),
) -> Any:
    return await scheduling_service.schedule_patient(
        availability_id=request.availability_id,
        patient_user=patient,
    )
