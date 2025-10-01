from uuid import UUID

from pydantic import BaseModel


class BlockCreateRequest(BaseModel):
    professional_id: UUID
    start_time: str
    end_time: str
