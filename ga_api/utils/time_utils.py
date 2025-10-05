from datetime import datetime, timedelta

from starlette import status
from starlette.exceptions import HTTPException

MAX_TIME_INTERVAL_HOURS = 2
INVALID_TIME_ERROR = "Invalid time interval"
INVALID_TIME_INTERVAL_ERROR = (
    "Maximum time interval between start and end must be 2 hours"
)


class TimeUtils:

    @staticmethod
    def validate_start_and_end_times(
        start: datetime,
        end: datetime,
        error_when_equals: bool = True,
    ) -> None:
        """Validates if start time is greater than end time.
        Raise HTTPException 400 if invalid.
        :param start: datetime
        :param end: datetime
        :param error_when_equals: bool (default True)
        """
        if error_when_equals and start == end:
            raise HTTPException(
                detail=INVALID_TIME_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if start > end:
            raise HTTPException(
                detail=INVALID_TIME_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def validate_max_two_hours(start: datetime, end: datetime) -> None:
        interval = end - start

        if interval > timedelta(hours=MAX_TIME_INTERVAL_HOURS):
            raise HTTPException(
                detail=INVALID_TIME_INTERVAL_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def is_interval(start: datetime | None, end: datetime | None) -> bool:
        return isinstance(start, datetime) and isinstance(end, datetime)
