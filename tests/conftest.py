from typing import Any, AsyncGenerator, List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from pydantic.v1 import EmailStr
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ga_api.db.base import Base
from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.dependencies import get_db_session
from ga_api.db.models.users import UserCreate
from ga_api.db.sql_scripts import SqlScripts
from ga_api.db.utils import create_database, drop_database
from ga_api.settings import settings
from ga_api.web.application import get_app
from tests.factories.user_factory import UserFactory


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from ga_api.db.meta import meta
    from ga_api.db.models import load_all_models

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
        await conn.execute(text(SqlScripts.create_root_admin()))

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac


async def register_user(client: AsyncClient, request: UserCreate) -> None:
    await client.post(
        "/api/auth/register",
        json=request.model_dump(mode="json"),
    )


async def login_user(client: AsyncClient, email: str, password: str) -> str:
    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


async def login_user_admin(client: AsyncClient) -> str:
    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": "admin@admin.com", "password": "admin"},
    )
    return response.json()["access_token"]


async def register_and_login_default_user(client: AsyncClient) -> str:
    user_request: UserCreate = UserFactory.create_default_user_request()
    await register_user(client, user_request)
    return await login_user(
        client, email=str(user_request.email), password=user_request.password
    )


async def save_and_expect(
    dao: AbstractDAO[Any],
    object_to_save: Base | List[Base],
    expected_quantity: int,
) -> None:
    object_list: bool = isinstance(object_to_save, list)

    if object_list:
        await dao.save_all(object_to_save)

    else:
        await dao.save(object_to_save)

    result = await dao.find_all()

    expected_type: Any = (
        type(object_to_save[0]) if object_list else type(object_to_save)
    )

    assert len(result) == expected_quantity
    assert all(isinstance(item, expected_type) for item in result)
