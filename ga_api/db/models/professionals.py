from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ga_api.db.base import Base
from ga_api.enums.availability_status import AvailabilityStatus


# Tabela de associação para a relação Many-to-Many
professionals_specialities = Table(
    "professionals_specialities",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("professional_id", Integer, ForeignKey("professionals.id")),
    Column("speciality_id", Integer, ForeignKey("specialities.id")),
)


class Professional(Base):
    __tablename__ = "professionals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    updated_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    specialities: Mapped[List["Speciality"]] = relationship(secondary=professionals_specialities, back_populates="professionals")
    availabilities: Mapped[List["Availability"]] = relationship(back_populates="professional")
    blocks: Mapped[List["Block"]] = relationship(back_populates="professional")


class Speciality(Base):
    __tablename__ = "specialities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    professionals: Mapped[List["Professional"]] = relationship(secondary=professionals_specialities, back_populates="specialities")


class Availability(Base):
    __tablename__ = "availabilities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    status: Mapped[AvailabilityStatus] = mapped_column(SQLAlchemyEnum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    professional_id: Mapped[int] = mapped_column(ForeignKey("professionals.id"))
    patient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    updated_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    professional: Mapped["Professional"] = relationship(back_populates="availabilities")


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    professional_id: Mapped[int] = mapped_column(ForeignKey("professionals.id"))
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    professional: Mapped["Professional"] = relationship(back_populates="blocks")
