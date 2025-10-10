# ga_api/services/professional_service.py

import uuid
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.professional_dao import ProfessionalDAO
from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.professionals_model import Professional
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.professionals.request.professional_create_request import (
    ProfessionalCreateRequest,
)
from ga_api.web.api.professionals.request.professional_update_request import (
    ProfessionalUpdateRequest,
)
from ga_api.web.api.professionals.response.professional_block_response import (
    ProfessionalBlockResponse,
)


class ProfessionalService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.professional_dao = ProfessionalDAO(session)
        self.speciality_dao = SpecialityDAO(session)

    async def create_professional(
        self,
        request: ProfessionalCreateRequest,
        admin_user: User,
    ) -> Professional:

        new_professional: Professional = Professional(
            full_name=request.full_name,
            bio=request.bio,
            phone=request.phone,
            email=request.email,
            is_enabled=request.is_enabled,
            specialities=[],
        )

        if request.specialities:
            all_ids_exist = await self.speciality_dao.all_ids_exist_in(
                request.specialities,
            )

            if not all_ids_exist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more specialities specified does not exist.",
                )

            new_professional.specialities = await self.speciality_dao.find_all_by_ids(
                request.specialities,
            )

        AdminUtils.populate_admin_data(new_professional, admin_user)
        return await self.professional_dao.save(new_professional)

    async def update_professional(
        self,
        professional_id: uuid.UUID,
        request: ProfessionalUpdateRequest,
        admin_user: User,
    ) -> Professional:
        professional = await self.professional_dao.find_by_id(
            professional_id,
        )
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional not found.",
            )
        if request.full_name is not None:
            professional.full_name = request.full_name

        if request.bio is not None:
            professional.bio = request.bio

        if request.is_enabled is not None:
            professional.is_enabled = request.is_enabled

        if request.specialities is not None:
            if len(request.specialities) == 0:
                professional.specialities = []

            else:
                all_ids_exist = await self.speciality_dao.all_ids_exist_in(
                    request.specialities,
                )
                if not all_ids_exist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="One or more specialities specified does not exist.",
                    )
                professional.specialities = await self.speciality_dao.find_all_by_ids(
                    request.specialities,
                )

        AdminUtils.populate_admin_data(professional, admin_user, update_only=True)
        return await self.professional_dao.save(professional)

    async def get_all_professionals_admin(
        self,
        limit: int,
        offset: int,
    ) -> List[ProfessionalBlockResponse]:
        professionals_and_blocked_list = (
            await self.professional_dao.find_all_with_specialities(limit, offset)
        )

        return [
            ProfessionalBlockResponse(professional=prof, is_blocked=is_blocked)  # type: ignore
            for prof, is_blocked in professionals_and_blocked_list
        ]

    async def get_all_professionals(
        self,
        limit: int,
        offset: int,
    ) -> List[ProfessionalBlockResponse]:
        professionals_and_blocked_list = (
            await self.professional_dao.find_all_with_specialities(
                limit,
                offset,
                only_enabled=True,
            )
        )

        return [
            ProfessionalBlockResponse(professional=prof, is_blocked=is_blocked)  # type: ignore
            for prof, is_blocked in professionals_and_blocked_list
        ]
