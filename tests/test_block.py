import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from tests.utils import login_user_admin
from uuid import UUID


@pytest.mark.anyio
async def test_create_block(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional_id = professional_id = UUID
    payload = {
        "professional_id": professional_id,
        "start_time": "2025-01-01T00:00:00Z",
        "end_time": "3025-12-29T23:59:59Z",
        "reason": "Teste de bloqueio",
    }
    response = await client.post("/api/admin/blocks/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()


@pytest.mark.anyio
async def test_delete_block(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional_id = professional_id = UUID
    payload = {
        "professional_id": professional_id,
        "start_time": "2025-01-01T00:00:00Z",
        "end_time": "3025-12-29T23:59:59Z",
        "reason": "Teste de bloqueio",
    }
    response = await client.post("/api/admin/blocks/", json=payload, headers=headers)
    block_id = response.json()["id"]

    response = await client.delete(f"/api/admin/blocks/{block_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
