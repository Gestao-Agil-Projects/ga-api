import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy import TIMESTAMP, Boolean, Date, String, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette.exceptions import HTTPException
from starlette.requests import Request

from ga_api.db.base import Base
from ga_api.db.dependencies import get_db_session
from ga_api.db.utils import create_generic_integrity_error_message
from ga_api.enums.consultation_frequency import ConsultationFrequency
from ga_api.enums.user_role import UserRole
from ga_api.settings import settings


class User(SQLAlchemyBaseUserTableUUID, Base):

    __tablename__ = "users"
    cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(String(200), nullable=True)
    is_first_access: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    frequency: Mapped[ConsultationFrequency] = mapped_column(
        SQLAlchemyEnum(ConsultationFrequency),
        nullable=False,
        default=ConsultationFrequency.AS_NEEDED,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole),
        nullable=False,
        default=UserRole.PATIENT,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserRead(schemas.BaseUser[uuid.UUID]):
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    full_name: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    frequency: ConsultationFrequency
    role: UserRole
    is_first_access: bool


class UserCreate(schemas.BaseUserCreate):
    cpf: str
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    full_name: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    is_first_access: Optional[bool] = False
    frequency: ConsultationFrequency = ConsultationFrequency.AS_NEEDED


class UserUpdate(schemas.BaseUserUpdate):
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None
    frequency: Optional[ConsultationFrequency] = None


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        session: AsyncSession = self.user_db.session  # type: ignore
        try:
            return await super().create(user_create, safe, request)

        except (IntegrityError, UserAlreadyExists) as e:
            await session.rollback()
            detail: str = create_generic_integrity_error_message(e)
            raise HTTPException(
                status_code=400,
                detail=detail,
            ) from e


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserDatabase:
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> UserManager:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    Return a JWTStrategy in orderto instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(secret=settings.users_secret, lifetime_seconds=None)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

backends = [
    auth_jwt,
]

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)

current_active_user = api_users.current_user(active=True)
