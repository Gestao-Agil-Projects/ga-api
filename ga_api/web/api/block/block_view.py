from typing import Annotated, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.dao.professional_dao import ProfessionalDAO
from ga_api.db.models.users import current_active_user
from ga_api.services.block_service import BlockService
from ga_api.web.api.block.request.block_request import BlockCreateRequest
from ga_api.web.api.block.response.block_response import BlockResponse

admin_router = APIRouter()


def get_block_service(
    block_dao: Annotated[BlockDAO, Depends()],
    professional_dao: Annotated[ProfessionalDAO, Depends()],
) -> BlockService:
    return BlockService(block_dao, professional_dao)


@admin_router.post("/", response_model=BlockResponse, status_code=201)
async def create_block_endpoint(
    user: Annotated[Any, Depends(current_active_user)],
    data: BlockCreateRequest,
    block_service: Annotated[BlockService, Depends(get_block_service)],
) -> BlockResponse:
    return await block_service.create_block(data, user)  # type: ignore


@admin_router.delete("/{block_id}", status_code=204)
async def delete_block_endpoint(
    block_id: UUID,
    block_service: Annotated[BlockService, Depends(get_block_service)],
) -> None:
    await block_service.delete_block(block_id)


@admin_router.get("/{professional_id}")
async def get_professional_blocks(
    professional_id: UUID,
    block_service: Annotated[BlockService, Depends(get_block_service)],
) -> List[BlockResponse]:
    return await block_service.get_all_blocks_from_professional(professional_id)  # type: ignore
