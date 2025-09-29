import enum

class AvailabilityStatus(str, enum.Enum):
    """
    Enum for the status of an availability slot.
    """
    AVAILABLE = "available"
    TAKEN = "taken"
    COMPLETED = "completed"
    CANCELED = "canceled"
