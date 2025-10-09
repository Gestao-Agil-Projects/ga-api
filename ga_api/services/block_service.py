from typing import Optional
from uuid import UUID

from starlette import status
from starlette.exceptions import HTTPException

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.dao.professional_dao import ProfessionalDAO
from ga_api.db.models.block_model import Block
from ga_api.db.models.professionals_model import Professional
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.block.request.block_request import BlockCreateRequest


class BlockService:
    def __init__(self, block_dao: BlockDAO, professional_dao: ProfessionalDAO) -> None:
        self.block_dao = block_dao
        self.professional_dao = professional_dao

    async def create_block(self, data: BlockCreateRequest, user: User) -> Block:
        professional: Optional[Professional] = await self.professional_dao.find_by_id(
            data.professional_id,
        )
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional not found",
            )

        block: Block = Block(**data.model_dump())

        AdminUtils.populate_admin_data(block, user)
        return await self.block_dao.save(block)

    async def delete_block(self, block_id: UUID) -> None:
        await self.block_dao.delete_by_id(block_id)
