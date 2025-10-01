from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.models.users import User
from ga_api.enums.user_role import UserRole
from ga_api.services.block_service import BlockService
from ga_api.web.api.block.request.block_request import BlockCreateRequest
from ga_api.web.api.block.response.block_response import BlockResponse

router = APIRouter()


# Dummy admin dependency (replace with real auth)
def get_current_admin_user() -> dict[str, UserRole | str]:
    # Simula usuario admin
    return {"role": UserRole.ADMIN, "id": "admin-id"}


def admin_required(user: User = Depends(get_current_admin_user)) -> None:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


def get_block_service(block_dao: Annotated[BlockDAO, Depends()]) -> BlockService:
    return BlockService(block_dao)


@router.post("/", response_model=BlockResponse, status_code=201)
async def create_block_endpoint(
    user: Annotated[Any, Depends(admin_required)],
    data: BlockCreateRequest,
    block_service: Annotated[BlockService, Depends(get_block_service)],
) -> BlockResponse:
    block = await block_service.create_block(data, user["id"])
    return BlockResponse(
        id=block.id,
        professional_id=block.professional_id,
        start_time=block.start_time.isoformat(),
        end_time=block.end_time.isoformat(),
    )


@router.delete("/{block_id}", status_code=204)
async def delete_block_endpoint(
    user: Annotated[Any, Depends(admin_required)],
    block_id: int,
    block_service: Annotated[BlockService, Depends(get_block_service)],
) -> None:
    await block_service.delete_block(block_id)
