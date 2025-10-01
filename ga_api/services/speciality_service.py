from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.models.speciality_model import Speciality
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.speciality.request.speciality_request import SpecialityRequest


class SpecialityService:
    def __init__(self, speciality_dao: SpecialityDAO) -> None:
        self.speciality_dao = speciality_dao

    async def create_speciality(self, user: User, request: SpecialityRequest ) -> None:
        AdminUtils.validate_user_is_admin(user)
        speciality = Speciality(**request.model_dump(exclude_unset=True))
        await self.speciality_dao.save(speciality)

    async def get_speciality_models(
        self,
        limit: int,
        offset: int,
        speciality_id: UUID | None,
    ) -> List[Speciality]:
        if not speciality_id:
            return await self.speciality_dao.find_all(limit, offset)

        speciality: Optional[Speciality] = await self.speciality_dao.find_by_id(speciality_id)

        return [speciality] if speciality else []

    async def delete_speciality(self, speciality_id: UUID ) -> None:
        await self.speciality_dao.delete_by_id(speciality_id)


    async def update_speciality(self, user: User, speciality_id: UUID, request: SpecialityRequest) -> Speciality:
        AdminUtils.validate_user_is_admin(user)
        speciality: Optional[Speciality] = await self.speciality_dao.find_by_id(speciality_id)

        if not speciality:
            raise HTTPException(
                detail="Speciality not found",
                status_code=404,
            )

        return await self.speciality_dao.update(speciality, request.model_dump())
