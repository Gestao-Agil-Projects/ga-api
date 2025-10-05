import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ga_api.db.base import Base

if TYPE_CHECKING:
    from ga_api.db.models.professionals_model import Professional


class Speciality(Base):
    __tablename__ = "specialities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    professionals: Mapped[List["Professional"]] = relationship(
        "Professional",
        secondary="professionals_specialities",
        back_populates="specialities",
    )
