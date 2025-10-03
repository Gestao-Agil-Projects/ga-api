# ga_api/services/professional_service.py

import uuid
from datetime import datetime
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


class ProfessionalService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.professional_dao = ProfessionalDAO(session)
        self.speciality_dao = SpecialityDAO(session)

    async def create_professional(
        self,
        professional_create_request: ProfessionalCreateRequest,
        admin_user: User,
    ) -> Professional:
        AdminUtils.validate_user_is_admin(admin_user)

        professional_data = professional_create_request.model_dump()
        speciality_ids = professional_data.pop("specialities", [])

        new_professional = Professional(**professional_data)

        if speciality_ids:
            specialities = []
            for speciality_id in speciality_ids:
                if speciality_id:
                    speciality = await self.speciality_dao.find_by_id(speciality_id)
                    if speciality:
                        specialities.append(speciality)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Especialidade com id "
                            f"{speciality_id} não encontrada.",
                        )
            new_professional.specialities = specialities

        AdminUtils.populate_admin_data(new_professional, admin_user)
        return await self.professional_dao.save(new_professional)

    async def update_professional(
        self,
        professional_id: uuid.UUID,
        professional_update_request: ProfessionalUpdateRequest,
        admin_user: User,
    ) -> Professional:
        AdminUtils.validate_user_is_admin(admin_user)
        professional = await self.professional_dao.find_by_id(
            professional_id,
        )
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profissional nao encontrado.",
            )
        if professional_update_request.full_name is not None:
            professional.full_name = professional_update_request.full_name

        if professional_update_request.bio is not None:
            professional.bio = professional_update_request.bio

        professional.updated_at = datetime.now()
        professional.updated_by_admin_id = admin_user.id

        return professional

    async def get_all_professionals(
        self,
        admin_user: User,
    ) -> List[Professional]:
        AdminUtils.validate_user_is_admin(admin_user)
        return await self.professional_dao.get_all_with_specialities()
