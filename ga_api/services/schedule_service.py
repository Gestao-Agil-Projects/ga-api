from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.users import User
from ga_api.enums.availability_status import AvailabilityStatus
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.schedule.request.admin_schedule_request import AdminScheduleRequest
from ga_api.web.api.schedule.request.patient_schedule_request import (
    PatientScheduleRequest,
)


class SchedulingService:
    def __init__(
        self,
        availability_dao: AvailabilityDAO = Depends(),
        user_dao: UserDAO = Depends(),
    ) -> None:
        self.availability_dao = availability_dao
        self.user_dao = user_dao

    async def schedule_for_patient_by_admin(
        self,
        request: AdminScheduleRequest,
        admin_user: User,
    ) -> Availability:

        availability = await self._get_and_validate_availability(
            request.availability_id,
        )
        patient = await self.user_dao.find_by_email(str(request.email))

        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found.",
            )

        if await self.availability_dao.check_double_appointment(
            patient.id,
            availability.start_time,
            availability.end_time,
        ):
            raise HTTPException(
                status_code=409,
                detail="Patient already has a schedule conflicting.",
            )

        update_data = {
            "patient_id": patient.id,
            "status": AvailabilityStatus.TAKEN,
        }
        AdminUtils.populate_admin_data(availability, admin_user, update_only=True)

        return await self.availability_dao.update(availability, update_data)

    async def schedule_patient(
        self,
        request: PatientScheduleRequest,
        patient_user: User,
    ) -> Availability:
        availability = await self._get_and_validate_availability(
            request.availability_id,
        )

        if await self.availability_dao.check_double_appointment(
            patient_user.id,
            availability.start_time,
            availability.end_time,
        ):
            raise HTTPException(
                status_code=409,
                detail="You already have a schedule conflicting with this new one.",
            )

        update_data = {
            "patient_id": patient_user.id,
            "status": AvailabilityStatus.TAKEN,
        }
        return await self.availability_dao.update(availability, update_data)

    async def get_user_schedules(
        self,
        user: User,
        limit: int,
        offset: int,
    ) -> List[Availability]:
        """
        Retorna os agendamentos (availabilities) do usuário autenticado com paginação.
        """
        return await self.availability_dao.find_by_patient_id(
            user.id,
            limit=limit,
            offset=offset,
        )

    async def _get_and_validate_availability(
        self,
        availability_id: UUID,
    ) -> Availability:
        availability = await self.availability_dao.find_by_id(availability_id)
        if not availability:
            raise HTTPException(
                status_code=404,
                detail="Availability not found.",
            )
        if availability.status != AvailabilityStatus.AVAILABLE:
            raise HTTPException(
                status_code=400,
                detail="This availability is not available.",
            )
        return availability
