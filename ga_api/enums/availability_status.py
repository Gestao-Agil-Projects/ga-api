import enum


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    TAKEN = "taken"
    COMPLETED = "completed"
    CANCELED = "canceled"
