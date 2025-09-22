import enum

class ConsultationFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"
