import enum

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    ADMIN = "admin"