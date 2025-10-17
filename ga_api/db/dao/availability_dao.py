from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, exists, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.block_model import Block
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

    async def find_all_not_blocked(
        self,
        limit: int,
        offset: int,
        professional_id: Optional[UUID] = None,
        status: Optional[AvailabilityStatus] = None,
        after: Optional[datetime] = None,
    ) -> List[Availability]:
        subq = (
            select(1)
            .where(
                and_(
                    Block.professional_id == Availability.professional_id,
                    Block.start_time < Availability.end_time,
                    Block.end_time > Availability.start_time,
                ),
            )
            .correlate(Availability)
        )

        conditions = [not_(exists(subq))]

        if professional_id:
            conditions.append(Availability.professional_id == professional_id)
        if status:
            conditions.append(Availability.status == status)
        if after:
            conditions.append(Availability.start_time > after)

        query = (
            select(Availability).where(and_(*conditions)).offset(offset).limit(limit)
        )

        result = await self._session.execute(query)
        return result.scalars().all()  # type: ignore
