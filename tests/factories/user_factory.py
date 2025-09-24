import random
from ga_api.db.models.users import UserCreate


class UserFactory:

    @staticmethod
    def generate_random_cpf() -> str:
        return "".join([str(random.randint(0, 9)) for _ in range(11)])

    @staticmethod
    def create_default_user_create():
        return UserCreate(
            email="mock@mail.com",  # type: ignore
            password="password123",
            full_name="john",
            cpf=UserFactory.generate_random_cpf(),
        )

    @staticmethod
    def create_user_create(
        full_name: str,
        cpf: str,
        email: str = None,
        password: str = None,
    ) -> UserCreate:
        return UserCreate(
            email=email or f"{UserFactory.generate_random_cpf()}@mail.com",  # type: ignore
            password=password or "password123",
            full_name=full_name,
            cpf=cpf,
        )
