import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import login_user_admin, register_and_login_default_user


@pytest.mark.anyio
async def test_get_all_patients_as_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    url = "/api/admin/patients"
    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_all_patients_as_non_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await register_and_login_default_user(client)
    url = "/api/admin/patients"
    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_get_all_patients_unauthenticated(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    url = "/api/admin/patients"
    response = await client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_all_patients_pagination(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)

    for i in range(15):
        await register_and_login_default_user(
            client,
            email=f"patient{i}@example.com",
            cpf=f"123.456.789-{i:02d}",
        )

    url_page1 = "/api/admin/patients?skip=5&limit=5"
    response1 = await client.get(url_page1, headers={"Authorization": f"Bearer {token}"})
    assert response1.status_code == status.HTTP_200_OK
    assert len(response1.json()) == 5

    url_page2 = "/api/admin/patients?skip=10&limit=5"
    response2 = await client.get(url_page2, headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == status.HTTP_200_OK
    assert len(response2.json()) <= 5
