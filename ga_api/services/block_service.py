from uuid import UUID

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.models.block_model import Block
from ga_api.db.models.users import User
from ga_api.utils.admin_utils import AdminUtils
from ga_api.web.api.block.request.block_request import BlockCreateRequest


class BlockService:
    def __init__(self, block_dao: BlockDAO) -> None:
        self.block_dao = block_dao

    async def create_block(self, data: BlockCreateRequest, user: User) -> Block:
        AdminUtils.validate_user_is_admin(user)

        # todo: fazer uma query no professionals e ver se existe o profissional

        block: Block = Block(**data.model_dump())

        AdminUtils.populate_admin_data(block, user)
        return await self.block_dao.save(block)

    async def delete_block(self, block_id: UUID, user: User) -> None:
        AdminUtils.validate_user_is_admin(user)

        await self.block_dao.delete_by_id(block_id)
