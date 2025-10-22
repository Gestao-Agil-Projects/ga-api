from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status

from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.models.speciality_model import Speciality
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.speciality.request.speciality_request import SpecialityRequest


class SpecialityService:
    def __init__(self, speciality_dao: SpecialityDAO) -> None:
        self.speciality_dao = speciality_dao

    async def create_speciality(
        self,
        request: SpecialityRequest,
    ) -> Speciality:
        request.title = request.title.lower()
        await self._validate_title(request.title)

        speciality = Speciality(**request.model_dump(exclude_unset=True))
        return await self.speciality_dao.save(speciality)

    async def get_speciality_models(
        self,
        limit: int,
        offset: int,
        speciality_id: UUID | None,
    ) -> List[Speciality]:
        if not speciality_id:
            return await self.speciality_dao.find_all(limit, offset)

        speciality: Optional[Speciality] = await self.speciality_dao.find_by_id(
            speciality_id,
        )

        return [speciality] if speciality else []

    async def delete_speciality(self, speciality_id: UUID) -> None:
        await self.speciality_dao.delete_by_id(speciality_id)

    async def update_speciality(
        self,
        user: User,
        speciality_id: UUID,
        request: SpecialityRequest,
    ) -> Speciality:
        speciality: Optional[Speciality] = await self.speciality_dao.find_by_id(
            speciality_id,
        )

        if not speciality:
            raise HTTPException(
                detail="Speciality not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        await self._validate_title(request.title.lower())

        speciality.title = request.title.lower()
        AdminUtils.populate_admin_data(speciality, user, update_only=True)

        return await self.speciality_dao.save(speciality)

    async def _validate_title(self, title: str) -> None:
        speciality = await self.speciality_dao.find_by_title(title)
        if speciality:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Speciality with this title already exists.",
            )
