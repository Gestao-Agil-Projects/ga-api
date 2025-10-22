import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories.user_factory import UserFactory
from ga_api.db.models.users import UserCreate
from tests.utils import login_user_admin, register_and_login_default_user, register_user

GET_PATIENTS_URI = "/api/admin/users/patients"


@pytest.mark.anyio
async def test_get_all_patients_as_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)

    response = await client.get(
        GET_PATIENTS_URI, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_all_patients_as_non_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await register_and_login_default_user(client)

    response = await client.get(
        GET_PATIENTS_URI, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_get_all_patients_unauthenticated(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:

    response = await client.get(GET_PATIENTS_URI)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_all_patients_pagination(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)

    for i in range(3):
        user_request: UserCreate = UserFactory.create_random_user_request()

        await register_user(client, user_request)

    url_page1 = "/api/admin/users/patients?skip=0&limit=2"
    response1 = await client.get(
        url_page1, headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == status.HTTP_200_OK
    assert len(response1.json()) == 2

    url_page2 = "/api/admin/users/patients?skip=1&limit=1"
    response2 = await client.get(
        url_page2, headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == status.HTTP_200_OK
    assert len(response2.json()) == 1
