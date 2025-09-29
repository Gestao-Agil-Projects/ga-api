import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.dummy_dao import DummyDAO
from ga_api.db.models.dummy_model import DummyModel
from ga_api.web.api.dummy.request.dummy_request import DummyRequest
from tests.utils import register_and_login_default_user, save_and_expect


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance creation."""
    url = fastapi_app.url_path_for("create_dummy_model")
    test_name = uuid.uuid4().hex
    response = await client.put(url, json={"name": test_name, "age": 42})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = DummyDAO(dbsession)
    instances = await dao.filter(name=test_name)
    assert len(instances) == 1
    assert instances[0].name == test_name


@pytest.mark.anyio
async def test_getting_list(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance retrieval without dummy_id (list)."""
    token: str = await register_and_login_default_user(client)
    dao = DummyDAO(dbsession)

    test_name1 = uuid.uuid4().hex
    test_name2 = uuid.uuid4().hex

    dummy1 = DummyModel(name=test_name1, age=10)
    dummy2 = DummyModel(name=test_name2, age=20)

    await save_and_expect(dao, [dummy1, dummy2], 2)

    url = fastapi_app.url_path_for("get_dummy_models")
    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    dummies = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(dummies) == 2
    assert dummies[0]["name"] is not None
    assert dummies[1]["name"] is not None


@pytest.mark.anyio
async def test_getting_by_id_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy retrieval by id when it exists."""
    token: str = await register_and_login_default_user(client)

    dao = DummyDAO(dbsession)

    dummy = DummyModel(name="by_id", age=77)

    await save_and_expect(dao, dummy, 1)

    url = fastapi_app.url_path_for("get_dummy_models")
    response = await client.get(
        url,
        params={"dummy_id": dummy.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["id"] == dummy.id
    assert data[0]["name"] == "by_id"


@pytest.mark.anyio
async def test_getting_by_id_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests dummy retrieval by id when it does not exist."""
    token: str = await register_and_login_default_user(client)

    url = fastapi_app.url_path_for("get_dummy_models")
    response = await client.get(
        url,
        params={"dummy_id": 999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.anyio
async def test_deletion_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests dummy deletion by id."""
    token: str = await register_and_login_default_user(client)
    dao = DummyDAO(dbsession)

    dummy = DummyModel(name="to_delete", age=99)

    await save_and_expect(dao, dummy, 1)

    url = fastapi_app.url_path_for("delete_dummy_model")
    response = await client.delete(
        url,
        params={"dummy_id": dummy.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await dao.find_all()


@pytest.mark.anyio
async def test_deletion_by_name(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests dummy deletion by name."""
    token: str = await register_and_login_default_user(client)
    dao = DummyDAO(dbsession)

    dummy = DummyModel(name="to_delete_by_name", age=50)

    await save_and_expect(dao, dummy, 1)

    url = fastapi_app.url_path_for("delete_dummy_model")
    response = await client.delete(
        url,
        params={"dummy_name": "to_delete_by_name"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await dao.find_all()


@pytest.mark.anyio
async def test_deletion_with_no_params(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """Tests deletion request without id or name (no-op)."""
    token: str = await register_and_login_default_user(client)

    url = fastapi_app.url_path_for("delete_dummy_model")
    response = await client.delete(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_update_dummy_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests dummy update success."""
    token: str = await register_and_login_default_user(client)
    dao = DummyDAO(dbsession)

    dummy = DummyModel(name="before_update", age=20)

    await save_and_expect(dao, dummy, 1)

    request = DummyRequest(
        name="after_update",
        age=25,
    )

    url = fastapi_app.url_path_for("update_dummy_model")
    response = await client.patch(
        url,
        params={"dummy_id": dummy.id},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("name") == "after_update"
    assert not data.get("age")

    updated = await dao.find_by_id(dummy.id)
    assert updated.name == "after_update"
    assert updated.age == 25


@pytest.mark.anyio
async def test_update_dummy_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """Tests update of non-existing dummy raises 404."""
    token: str = await register_and_login_default_user(client)

    url = fastapi_app.url_path_for("update_dummy_model")
    response = await client.patch(
        url,
        params={"dummy_id": 999999},
        json={"name": "does_not_matter", "age": 10},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Dummy not found"
