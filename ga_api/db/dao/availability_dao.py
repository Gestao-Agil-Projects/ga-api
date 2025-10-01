from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.availability_model import Availability


class AvailabilityDAO(AbstractDAO[Availability]):
    """Class for accessing availability table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        super().__init__(model=Availability, session=session)
