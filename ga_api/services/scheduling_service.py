from uuid import UUID

from fastapi import Depends, HTTPException

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.users import User
from ga_api.enums.availability_status import AvailabilityStatus


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
        availability_id: UUID,
        patient_email: str,
        admin_user: User,
    ) -> Availability:
        availability = await self._get_and_validate_availability(availability_id)
        patient = await self.user_dao.find_by_email(patient_email)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Paciente com o e-mail fornecido não encontrado.",
            )

        if await self.availability_dao.check_double_appointment(
            patient.id,
            availability.start_time,
            availability.end_time,
        ):
            raise HTTPException(
                status_code=409,
                detail="O paciente já possui um agendamento conflitante neste horário.",
            )

        update_data = {
            "patient_id": patient.id,
            "status": AvailabilityStatus.TAKEN,
            "updated_by_admin_id": admin_user.id,
        }
        return await self.availability_dao.update(availability, update_data)

    async def schedule_patient(
        self,
        *,
        availability_id: UUID,
        patient_user: User,
    ) -> Availability:
        availability = await self._get_and_validate_availability(availability_id)

        if await self.availability_dao.check_double_appointment(
            patient_user.id,
            availability.start_time,
            availability.end_time,
        ):
            raise HTTPException(
                status_code=409,
                detail="Você já possui um agendamento conflitante neste horário.",
            )

        update_data = {
            "patient_id": patient_user.id,
            "status": AvailabilityStatus.TAKEN,
            "updated_by_admin_id": None,
        }
        return await self.availability_dao.update(availability, update_data)

    async def _get_and_validate_availability(
        self,
        availability_id: UUID,
    ) -> Availability:
        availability = await self.availability_dao.find_by_id(availability_id)
        if not availability:
            raise HTTPException(
                status_code=404,
                detail="Disponibilidade não encontrada.",
            )
        if availability.status != AvailabilityStatus.AVAILABLE:
            raise HTTPException(
                status_code=400,
                detail="Este horário não está disponível.",
            )
        return availability
