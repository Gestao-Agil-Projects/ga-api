from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator

from ga_api.enums.availability_status import AvailabilityStatus


class UpdateAvailabilityRequest(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[AvailabilityStatus] = None

    @model_validator(mode="after")
    def validate_all(self) -> "UpdateAvailabilityRequest":
        self._validate_not_empty()
        self._validate_interval()
        return self

    def _validate_not_empty(self) -> None:
        if all(getattr(self, field) is None for field in self.model_fields):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided",
            )

    def _validate_interval(self) -> None:
        if (self.start_time is None) ^ (self.end_time is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time and end_time must both be provided or both omitted",
            )
