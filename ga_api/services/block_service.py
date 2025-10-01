from datetime import datetime

from ga_api.db.dao.block_dao import BlockDAO
from ga_api.db.models.block_model import BlockModel
from ga_api.web.api.block.request.block_request import BlockCreateRequest


class BlockService:
    def __init__(self, block_dao: BlockDAO) -> None:
        self.block_dao = block_dao

    async def create_block(self, data: BlockCreateRequest, admin_id: int) -> BlockModel:
        block = BlockModel(
            professional_id=data.professional_id,
            start_time=datetime.fromisoformat(data.start_time),
            end_time=datetime.fromisoformat(data.end_time),
            created_by_admin_id=admin_id,
        )
        return await self.block_dao.save_block(block)

    async def delete_block(self, block_id: int) -> None:
        await self.block_dao.remove_block_by_id(block_id)
