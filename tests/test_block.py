from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.models.block_model import Block
from ga_api.db.models.professionals_model import Professional
from ga_api.web.api.block.request.block_request import BlockCreateRequest
from tests.utils import (
    login_user_admin,
    register_and_login_default_user,
    inject_default_professional,
)


@pytest.mark.anyio
async def test_create_block(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    response = await client.post(
        "/api/admin/blocks/", json=request.model_dump(mode="json"), headers=headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()


@pytest.mark.anyio
async def test_create_block_with_patient_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await register_and_login_default_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    response = await client.post(
        "/api/admin/blocks/", json=request.model_dump(mode="json"), headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_create_block_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    headers = {"Authorization": f"Bearer foo_token"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    response = await client.post(
        "/api/admin/blocks/", json=request.model_dump(mode="json"), headers=headers
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_create_block_with_invalid_professional_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    request = BlockCreateRequest(
        professional_id=uuid4(),
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    response = await client.post(
        "/api/admin/blocks/", json=request.model_dump(mode="json"), headers=headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_create_block_with_end_time_before_start_time(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional: Professional = await inject_default_professional(dbsession)

    # Enviar dados diretamente como dict, sem criar o modelo
    request_data = {
        "professional_id": str(professional.id),
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "reason": "teste de bloqueio",
    }

    response = await client.post(
        "/api/admin/blocks/", json=request_data, headers=headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_delete_block(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    block_dao = BlockDAO(dbsession)

    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    await client.post(
        "/api/admin/blocks/", json=request.model_dump(mode="json"), headers=headers
    )

    all_blocks: List[Block] = await block_dao.find_all()
    block = all_blocks[0]

    response = await client.delete(f"/api/admin/blocks/{block.id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_delete_block_with_patient_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    block_dao = BlockDAO(dbsession)

    # Criar o bloco com admin
    admin_token = await login_user_admin(client)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    await client.post(
        "/api/admin/blocks/",
        json=request.model_dump(mode="json"),
        headers=admin_headers,
    )

    all_blocks: List[Block] = await block_dao.find_all()
    block = all_blocks[0]

    # Tentar deletar com usuário paciente
    patient_token = await register_and_login_default_user(client)
    patient_headers = {"Authorization": f"Bearer {patient_token}"}

    response = await client.delete(
        f"/api/admin/blocks/{block.id}", headers=patient_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_delete_block_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    block_dao = BlockDAO(dbsession)

    # Criar o bloco com admin
    admin_token = await login_user_admin(client)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    professional: Professional = await inject_default_professional(dbsession)

    request = BlockCreateRequest(
        professional_id=professional.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=1),
        reason="teste de bloqueio",
    )

    await client.post(
        "/api/admin/blocks/",
        json=request.model_dump(mode="json"),
        headers=admin_headers,
    )

    all_blocks: List[Block] = await block_dao.find_all()
    block = all_blocks[0]

    # Tentar deletar sem autenticação
    headers = {"Authorization": f"Bearer foo_token"}

    response = await client.delete(f"/api/admin/blocks/{block.id}", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_delete_block_not_found_invalid_uuid_format(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/api/admin/blocks/99999", headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_delete_block_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    token = await login_user_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/api/admin/blocks/{uuid4()}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
