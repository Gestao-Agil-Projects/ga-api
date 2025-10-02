from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BlockResponse(BaseModel):
    id: UUID
    professional_id: UUID
    start_time: datetime
    end_time: datetime
