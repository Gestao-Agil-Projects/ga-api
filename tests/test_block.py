from datetime import datetime, timedelta
from typing import List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.models.block_model import Block
from ga_api.web.api.block.request.block_request import BlockCreateRequest
from tests.utils import login_user_admin
from uuid import UUID

# TESTES DESABILITADOS POR CONTA DE EXIGIR O FLUXO DE CADASTRO DE PROFISSIONAL
# @pytest.mark.anyio
# async def test_create_block(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
# ) -> None:
#     token = await login_user_admin(client)
#     headers = {"Authorization": f"Bearer {token}"}
#
#     request = BlockCreateRequest(
#         professional_id="professional_id",
#         start_time=datetime.now(),
#         end_time=datetime.now() + timedelta(days=1),
#         reason="teste de bloqueio")
#
#     response = await client.post("/api/admin/blocks/",
#         json=request.model_dump(mode="json"),
#         headers=headers)
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert "id" in response.json()
#
#
# @pytest.mark.anyio
# async def test_delete_block(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
# ) -> None:
#
#     block_dao = BlockDAO(dbsession)
#
#     token = await login_user_admin(client)
#     headers = {"Authorization": f"Bearer {token}"}
#
#     request = BlockCreateRequest(
#         professional_id="professional_id",
#         start_time=datetime.now(),
#         end_time=datetime.now() + timedelta(days=1),
#         reason="teste de bloqueio")
#
#     await client.post("/api/admin/blocks/",
#         json=request.model_dump(mode="json"),
#         headers=headers)
#
#     all_blocks: List[Block] = await block_dao.find_all()
#     block = all_blocks[0]
#
#     response = await client.delete(f"/api/admin/blocks/{block.id}", headers=headers)
#
#     assert response.status_code == status.HTTP_204_NO_CONTENT
