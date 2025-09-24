from datetime import date

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.users import User, UserCreate
from tests.conftest import (
    register_and_login_default_user,
    register_user,
    save_and_expect,
)
from tests.factories.user_factory import UserFactory


@pytest.mark.anyio
async def test_register_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    email = "foo@mail.com"
    password = "pass123"
    full_name = "123"
    cpf = "123.456.789-12"

    user_create_request: UserCreate = UserCreate(
        email=email, password=password, full_name=full_name, cpf=cpf
    )  # type: ignore

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["email"] == email
    assert body["cpf"] == cpf
    assert "id" in body


@pytest.mark.anyio
async def test_register_user_partial_data(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    full_name = "Partial User"
    cpf = "123.456.789-12"
    email = f"{cpf}@mail.com"
    password = "partialpassword"
    bio="this is a bio"

    user_create_request: UserCreate = UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        cpf=cpf,
        bio=bio
    )

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["full_name"] == full_name
    assert body["cpf"] == cpf
    assert "id" in body


@pytest.mark.anyio
async def test_register_user_full_data(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_create_request: UserCreate = UserFactory.create_default_user_create()
    user_create_request.birth_date = date(2000,1,1).isoformat()
    user_create_request.phone = "11987654321"
    user_create_request.bio = "A full user bio."

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump_json(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["email"] == user_create_request.email
    assert body["full_name"] == user_create_request.full_name
    assert body["cpf"] == user_create_request.cpf
    assert body["birth_date"] == "2000-01-01"
    assert body["phone"] == "11987654321"
    assert body["bio"] == "A full user bio."
    assert "id" in body

    user_dao = UserDAO(dbsession)
    await save_and_expect(user_dao, User, 1)


@pytest.mark.anyio
async def test_register_user_without_full_name_returns_error(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    cpf = "123.456.789-12"
    email = f"{cpf}@mail.com"
    password = "password123"

    user_create_request: UserCreate = UserCreate(
        email=email,
        password=password,
        full_name=None,  # type: ignore
        cpf=cpf,
    )

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(exclude_unset=True),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert "full_name" in str(body)


@pytest.mark.anyio
async def test_register_user_without_cpf_returns_error(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    full_name = "No CPF User"
    email = "nocpf@mail.com"
    password = "password123"

    user_create_request: UserCreate = UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        cpf=None,  # type: ignore
    )

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(exclude_unset=True),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert "cpf" in str(body)


@pytest.mark.anyio
async def test_login_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_request: UserCreate = UserFactory.create_default_user_create()

    await register_user(client, user_request)

    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": user_request.email, "password": user_request.password},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.anyio
async def test_authenticated_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    email = "mock@mail.com"

    token = await register_and_login_default_user(client)

    response: Response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["email"] == email
    assert "id" in body


@pytest.mark.anyio
async def test_authenticated_request_must_error_when_not_auth(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    response: Response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer token123"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
