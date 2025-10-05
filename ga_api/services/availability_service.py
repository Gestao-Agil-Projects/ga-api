from datetime import datetime
from uuid import UUID

from starlette import status
from starlette.exceptions import HTTPException

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.utils.time_utils import TimeUtils
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest
from ga_api.web.api.availability.request.update_availability_request import (
    UpdateAvailabilityRequest,
)


class AvailabilityService:
    def __init__(self, availability_dao: AvailabilityDAO) -> None:
        self.availability_dao = availability_dao

    async def register_availability(
        self,
        request: AvailabilityRequest,
        user: User,
    ) -> Availability:
        # TODO: após demanda do cadastro de profissionais
        # validar com o professional_dao se o id especificado na request existe

        AdminUtils.validate_user_is_admin(user)
        TimeUtils.validate_start_and_end_times(request.start_time, request.end_time)
        TimeUtils.validate_max_two_hours(request.start_time, request.end_time)
        await self._validate_overlapping_times(request.start_time, request.end_time)

        availability: Availability = Availability(**request.model_dump())
        AdminUtils.populate_admin_data(availability, user)

        await self.availability_dao.save(availability)
        return availability

    async def update_availability(
        self,
        availability_id: UUID,
        request: UpdateAvailabilityRequest,
        user: User,
    ) -> Availability:
        AdminUtils.validate_user_is_admin(user)

        start, end = request.start_time, request.end_time

        if TimeUtils.is_interval(start, end):
            start_datetime: datetime = start  # type: ignore[assignment]
            end_datetime: datetime = end  # type: ignore[assignment]

            TimeUtils.validate_start_and_end_times(start_datetime, end_datetime)
            TimeUtils.validate_max_two_hours(start_datetime, end_datetime)

            await self._validate_overlapping_times(
                start_datetime,
                end_datetime,
                exclude_id=availability_id,
            )

        availability: Availability | None = await self.availability_dao.find_by_id(
            availability_id,
        )

        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability not found",
            )

        AdminUtils.populate_admin_data(availability, user, update_only=True)
        return await self.availability_dao.update(
            availability,
            request.model_dump(exclude_none=True),
        )

    async def _validate_overlapping_times(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_id: UUID | None = None,
    ) -> None:
        conditions = [
            Availability.start_time < end_time,
            Availability.end_time > start_time,
        ]

        if exclude_id:
            conditions.append(Availability.id != exclude_id)

        overlapping: bool = await self.availability_dao.exists(*conditions)

        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="time interval is conflicting with existent availability",
            )
