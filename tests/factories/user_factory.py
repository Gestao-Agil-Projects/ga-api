import random
from ga_api.db.models.users import UserCreate


class UserFactory:

    @staticmethod
    def create_default_user_create():
        return UserCreate(
            email="mock@mail.com",  # type: ignore
            password="password123",
            full_name="john",
            cpf="123.456.789-12",
            bio= "this is a bio"
        )

    @staticmethod
    def create_user_create(
        full_name: str,
        cpf: str,
        bio: str,
        email: str = None,
        password: str = None,
    ) -> UserCreate:
        return UserCreate(
            email=email,  # type: ignore
            password=password,
            full_name=full_name,
            cpf=cpf,
            bio=bio
        )
