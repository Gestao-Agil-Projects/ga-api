import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ga_api.db.base import Base

if TYPE_CHECKING:
    from ga_api.db.models.availability_model import Availability
    from ga_api.db.models.block_model import Block
    from ga_api.db.models.specialty_model import Speciality

professionals_specialities = Table(
    "professionals_specialities",
    Base.metadata,
    Column(
        "professional_id",
        UUID(as_uuid=True),
        ForeignKey("professionals.id"),
        primary_key=True,
    ),
    Column(
        "speciality_id",
        UUID(as_uuid=True),
        ForeignKey("specialities.id"),
        primary_key=True,
    ),
)


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"),
    )
    updated_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"),
    )
    specialities: Mapped[List["Speciality"]] = relationship(
        "Speciality",
        secondary=professionals_specialities,
        back_populates="professionals",
    )
    availabilities: Mapped[List["Availability"]] = relationship(
        "Availability",
        back_populates="professional",
    )
    blocks: Mapped[List["Block"]] = relationship(
        "Block",
        back_populates="professional",
    )
