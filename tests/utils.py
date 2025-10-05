from typing import Any, List

from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.base import Base
from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.models.availability_model import Availability
from ga_api.db.models.professionals_model import Professional
from ga_api.db.models.users import UserCreate
from tests.factories.user_factory import UserFactory


async def register_user(client: AsyncClient, request: UserCreate) -> None:
    await client.post(
        "/api/auth/register",
        json=request.model_dump(mode="json"),
    )


async def login_user(client: AsyncClient, email: str, password: str) -> str:
    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


async def login_user_admin(client: AsyncClient) -> str:
    response: Response = await client.post(
        "/api/auth/jwt/login",
        data={"username": "admin@admin.com", "password": "admin"},
    )
    return response.json()["access_token"]


async def register_and_login_default_user(client: AsyncClient) -> str:
    user_request: UserCreate = UserFactory.create_default_user_request()
    await register_user(client, user_request)
    return await login_user(
        client, email=str(user_request.email), password=user_request.password
    )


async def save_and_expect(
    dao: AbstractDAO[Any],
    object_to_save: Base | List[Base],
    expected_quantity: int,
) -> None:
    is_list: bool = isinstance(object_to_save, list)

    await dao.save_all(object_to_save) if is_list else await dao.save(object_to_save)
    result = await dao.find_all()
    expected_type: Any = type(object_to_save[0]) if is_list else type(object_to_save)

    assert len(result) == expected_quantity
    assert all(isinstance(item, expected_type) for item in result)


async def inject_default_professional(dbsession: AsyncSession) -> Professional:
    professional = Professional(full_name="John", email="john@mail.com")
    dbsession.add(professional)
    await dbsession.flush()
    return professional
