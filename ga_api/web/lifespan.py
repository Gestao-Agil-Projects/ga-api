from contextlib import asynccontextmanager
from logging import warning
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
)

from ga_api.db.meta import meta
from ga_api.db.models import load_all_models
from ga_api.db.sql_scripts import SqlScripts
from ga_api.settings import settings


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    load_all_models()
    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)
        await _create_root_admin(connection)
    await engine.dispose()


async def _create_root_admin(connection: AsyncConnection) -> None:
    warning("CREATING ROOT ADMIN. !!! MUST BE USED FOR DEVELOPMENT ONLY !!!")
    await connection.execute(text(SqlScripts.create_root_admin()))


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    _setup_db(app)
    await _create_tables()
    app.middleware_stack = app.build_middleware_stack()

    yield
    await app.state.db_engine.dispose()
