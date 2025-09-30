import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.models.users import UserCreate
from ga_api.enums.consultation_frequency import ConsultationFrequency
from ga_api.enums.user_role import UserRole
from tests.factories.user_factory import UserFactory
from tests.utils import login_user_admin, register_and_login_default_user, register_user


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
    assert "id" in body


@pytest.mark.anyio
async def test_register_user_partial_data(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_create_request: UserCreate = UserFactory.create_minimal_user_request()

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()

    assert "id" in body
    assert body["email"] == user_create_request.email
    assert body["full_name"] == user_create_request.full_name
    assert body["role"] == UserRole.PATIENT.value
    assert body["frequency"] == ConsultationFrequency.AS_NEEDED.value
    assert body.get("bio") is None
    assert body.get("phone") is None
    assert body.get("birth_date") is None


@pytest.mark.anyio
async def test_register_user_full_data(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_create_request: UserCreate = UserFactory.create_default_user_request()

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()

    assert "id" in body
    assert body["email"] == user_create_request.email
    assert body["full_name"] == user_create_request.full_name
    assert body["birth_date"] == user_create_request.birth_date.isoformat()
    assert body["phone"] == user_create_request.phone
    assert body["bio"] == user_create_request.bio
    assert body["role"] == UserRole.PATIENT.value
    assert "cpf" not in body


@pytest.mark.anyio
async def test_register_user_without_full_name_returns_error(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_create_request: UserCreate = UserFactory.create_default_user_request()
    user_create_request.full_name = None

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(mode="json"),
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
    user_create_request: UserCreate = UserFactory.create_default_user_request()
    user_create_request.cpf = None

    response: Response = await client.post(
        "/api/auth/register",
        json=user_create_request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert "cpf" in str(body)


@pytest.mark.anyio
async def test_register_user_with_registered_cpf_returns_error(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    await register_and_login_default_user(client)

    other_user_request: UserCreate = UserFactory.create_default_user_request()
    other_user_request.email = "foo@mail.com"  # type: ignore

    response: Response = await client.post(
        "/api/auth/register",
        json=other_user_request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body.get("detail") == "Cpf already exists."


@pytest.mark.anyio
async def test_login_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    user_request: UserCreate = UserFactory.create_default_user_request()

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


@pytest.mark.anyio
async def test_login_user_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": "admin@admin.com", "password": "admin"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"


@pytest.mark.anyio
async def test_authenticated_request_admin_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    token: str = await login_user_admin(client)

    response: Response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["email"] == "admin@admin.com"
    assert body["is_superuser"] == True
    assert body["is_active"] == True
    assert body["role"] == UserRole.PATIENT.value
    assert "id" in body
