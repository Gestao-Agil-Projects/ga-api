from starlette import status
from starlette.exceptions import HTTPException

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.utils.time_utils import TimeUtils
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest


class AvailabilityService:
    def __init__(self, availability_dao: AvailabilityDAO) -> None:
        self.availability_dao = availability_dao

    async def register_availability(
        self,
        request: AvailabilityRequest,
        user: User,
    ) -> Availability:
        AdminUtils.validate_user_is_admin(user)

        # TODO: após demanda do cadastro de profissionais
        # validar com o professional_dao se o id especificado na request existe

        TimeUtils.validate_start_and_end_times(request.start_time, request.end_time)
        TimeUtils.validate_max_two_hours(request.start_time, request.end_time)

        overlapping: bool = await self.availability_dao.exists(
            Availability.start_time < request.end_time,
            Availability.end_time > request.start_time,
        )

        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="time interval is conflicting with existent availability",
            )

        availability: Availability = Availability(**request.model_dump())
        AdminUtils.populate_admin_data(availability, user)

        await self.availability_dao.save(availability)
        return availability
