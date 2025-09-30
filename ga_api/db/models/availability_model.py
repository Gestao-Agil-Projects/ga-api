import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ga_api.db.base import Base
from ga_api.enums.availability_status import AvailabilityStatus

if TYPE_CHECKING:
    from ga_api.db.models.professionals_model import Professional
    from ga_api.db.models.users import User


class Availability(Base):
    __tablename__ = "availabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    status: Mapped[AvailabilityStatus] = mapped_column(
        SQLAlchemyEnum(AvailabilityStatus),
        default=AvailabilityStatus.AVAILABLE,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    professional_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("professionals.id"))
    patient_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    created_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"),
    )
    updated_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"),
    )

    professional: Mapped["Professional"] = relationship(
        "Professional",
        back_populates="availabilities",
    )

    patient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[patient_id])
