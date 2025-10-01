from uuid import UUID

from pydantic import BaseModel


class BlockResponse(BaseModel):
    id: UUID
    professional_id: UUID
    start_time: str
    end_time: str
