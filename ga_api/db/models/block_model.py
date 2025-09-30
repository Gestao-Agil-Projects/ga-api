import uuid
from datetime import datetime
from typing import Optional

from sql_alchemy.dialects.postgresql import UUID
from sqlalchemy import TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ga_api.db.base import Base
from ga_api.db.models.professionals_model import Professional


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    professional_id: Mapped[UUID] = mapped_column(ForeignKey("professionals.id"))
    created_by_admin_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))

    professional: Mapped["Professional"] = relationship(
        "Professional",
        back_populates="blocks",
    )
