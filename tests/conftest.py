from typing import Any, AsyncGenerator

from ga_api.db.models.users import User
from tests.factories.user_factory import UserFactory

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ga_api.db.dependencies import get_db_session
from ga_api.db.sql_scripts import SqlScripts
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
        if trans.is_active:
            await trans.rollback()
        await session.close()
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


@pytest.fixture
async def patient_user(client: AsyncClient, dbsession: AsyncSession) -> User:
    """
    Cria um usuário do tipo "paciente" através da API de registro.
    """
    user_request = UserFactory.create_default_user_request()

    await client.post("/api/auth/register", json=user_request.model_dump(mode="json"))

    user = (
        await dbsession.execute(select(User).where(User.email == user_request.email))
    ).scalar_one()
    return user


@pytest.fixture
async def cleint(client: AsyncClient, patient_user: User) -> AsyncClient:
    """
    Autentica o usuário paciente e retorna um client com o token de autorização.
    """
    login_data = {
        "username": patient_user.email,
        "password": "password123",  # A senha da sua UserFactory
    }

    response = await client.post("/api/auth/jwt/login", data=login_data)
    token_data = response.json()

    client.headers["Authorization"] = f"Bearer {token_data['access_token']}"
    return client
