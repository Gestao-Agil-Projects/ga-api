from typing import Any, AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ga_api.db.dependencies import get_db_session
from ga_api.db.utils import create_database, drop_database
from ga_api.settings import settings
from ga_api.web.application import get_app


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


async def register_user(
    client: AsyncClient,
    email: str,
    password: str,
    teste: str,
) -> None:
    await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "teste": teste},
    )


async def login_user(client: AsyncClient, email: str, password: str) -> str:
    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


async def register_and_login_default_user(client: AsyncClient) -> str:
    await register_user(
        client,
        email="mock@mail.com",
        password="password123",
        teste="test",
    )
    return await login_user(client, email="mock@mail.com", password="password123")


async def save_and_expect(
    dao: Any,
    object_to_save: Any,
    expected_quantity: int,
) -> None:
    dao.session.add(object_to_save)
    await dao.session.commit()

    result = await dao.session.execute(select(type(object_to_save)))
    all_data = result.scalars().all()

    assert len(all_data) == expected_quantity
    assert all(isinstance(item, type(object_to_save)) for item in all_data)
