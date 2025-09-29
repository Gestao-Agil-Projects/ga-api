from datetime import date

from ga_api.db.models.users import UserCreate
from ga_api.enums.consultation_frequency import ConsultationFrequency


class UserFactory:

    @staticmethod
    def create_default_user_request():
        return UserCreate(
            email="mock@mail.com",  # type: ignore
            password="password123",
            full_name="john",
            cpf="123.456.789-12",
            bio="this is a bio",
            birth_date=date(2000, 1, 1),
            frequency=ConsultationFrequency.AS_NEEDED,
            phone="51912345678",
            image_url=None,
        )

    @staticmethod
    def create_minimal_user_request():
        return UserCreate(
            email="minimal@example.com",  # type: ignore
            password="password123",
            full_name="Minimal User",
            cpf="111.222.333-44",
        )
