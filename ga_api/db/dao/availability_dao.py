from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.availability_model import Availability
from ga_api.enums.availability_status import AvailabilityStatus


class AvailabilityDAO(AbstractDAO[Availability]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Availability, session=session)

    async def check_double_appointment(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        conditions = [
            Availability.patient_id == user_id,
            Availability.status == AvailabilityStatus.TAKEN,
            Availability.start_time < end_time,
            Availability.end_time > start_time,
        ]

        return await self.exists(*conditions)

    async def find_by_patient_id(
        self,
        patient_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Availability]:
        result = await self._session.execute(
            select(Availability)
            .where(Availability.patient_id == patient_id)
            .limit(limit)
            .offset(offset),
        )
        return list(result.scalars().all())
