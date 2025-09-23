from ga_api.db.models.users import UserCreate


class UserFactory:

    @staticmethod
    def create_default_user_create():
        return UserCreate(
            email="mock@mail.com",  # type: ignore
            password="password123",
            full_name="john",
        )
