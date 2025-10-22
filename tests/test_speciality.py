import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.models.speciality_model import Speciality
from ga_api.web.api.speciality.request.speciality_request import SpecialityRequest
from tests.utils import (
    login_user_admin,
    register_and_login_default_user,
    save_and_expect,
)


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality creation with authentication."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    test_title = "Hello"
    request = SpecialityRequest(title=test_title)

    response = await client.post(
        url,
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    dao = SpecialityDAO(dbsession)
    instances = await dao.find_all()
    saved_object = instances[0]
    assert len(instances) == 1
    assert saved_object.title == test_title.lower()


@pytest.mark.anyio
async def test_creation_without_authentication_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that creating a speciality without authentication fails."""
    url = fastapi_app.url_path_for("create_speciality")
    request = SpecialityRequest(title="test")

    response = await client.post(url, json=request.model_dump())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_creation_with_non_admin_user_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that creating a speciality with a non-admin user fails."""
    token = await register_and_login_default_user(client)
    url = fastapi_app.url_path_for("create_speciality")
    request = SpecialityRequest(title="test")

    response = await client.post(
        url,
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_creation_saves_title_in_lowercase(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that the speciality title is saved in lowercase."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    mixed_case_title = "Cardiology"
    expected_lowercase_title = "cardiology"

    response = await client.post(
        url,
        json={"title": mixed_case_title},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    dao = SpecialityDAO(dbsession)
    instance = await dao.find_by_title(expected_lowercase_title)
    assert instance is not None
    assert instance.title == expected_lowercase_title


@pytest.mark.anyio
async def test_creation_duplicate_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that creating a speciality with a duplicate title fails."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    dao = SpecialityDAO(dbsession)

    existing_title = "dermatology"
    await dao.save(Speciality(title=existing_title))

    response = await client.post(
        url,
        json={"title": existing_title},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Speciality with this title already exists."


@pytest.mark.anyio
async def test_creation_duplicate_title_case_insensitive_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that the duplicate title check is case-insensitive."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    dao = SpecialityDAO(dbsession)

    await dao.save(Speciality(title="pediatrics"))

    response = await client.post(
        url,
        json={"title": "Pediatrics"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Speciality with this title already exists."


@pytest.mark.anyio
async def test_creation_with_empty_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that creating a speciality with an empty title fails."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")

    response = await client.post(
        url,
        json={"title": ""},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_getting_list(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality list retrieval."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    await dao.save(Speciality(title=uuid.uuid4().hex))
    await dao.save(Speciality(title=uuid.uuid4().hex))

    url = fastapi_app.url_path_for("get_speciality_models")
    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    specialities = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(specialities) >= 2


@pytest.mark.anyio
async def test_getting_list_with_pagination(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality list retrieval with pagination."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)

    for i in range(15):
        await dao.save(Speciality(title=f"speciality_{i}"))

    url = fastapi_app.url_path_for("get_speciality_models")
    response = await client.get(
        url,
        params={"limit": 5, "offset": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5

    response = await client.get(
        url,
        params={"limit": 5, "offset": 5},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5


@pytest.mark.anyio
async def test_getting_list_without_authentication_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that getting the list without authentication fails."""
    url = fastapi_app.url_path_for("get_speciality_models")
    response = await client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_getting_by_id_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality retrieval by id when it exists."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="get_by_id_test", id=uuid.uuid4())

    await save_and_expect(dao, speciality, 1)

    url = fastapi_app.url_path_for("get_speciality_models")
    response = await client.get(
        url,
        params={"speciality_id": str(speciality.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]["id"] == str(speciality.id)
    assert data[0]["title"] == "get_by_id_test"


@pytest.mark.anyio
async def test_getting_by_id_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests speciality retrieval by id when it does not exist."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("get_speciality_models")

    response = await client.get(
        url,
        params={"speciality_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == []


@pytest.mark.anyio
async def test_getting_by_invalid_uuid_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that getting by an invalid UUID fails."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("get_speciality_models")

    response = await client.get(
        url,
        params={"speciality_id": "invalid-uuid"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_update_speciality_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality update success."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="before_update")
    await dao.save(speciality)

    request = SpecialityRequest(title="After_Update")
    url = fastapi_app.url_path_for("update_speciality_model")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("title") == "after_update"

    updated = await dao.find_by_id(speciality.id)
    assert updated.title == "after_update"


@pytest.mark.anyio
async def test_update_speciality_without_authentication_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality without authentication fails."""
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="test")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="updated")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json=request.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_speciality_with_non_admin_user_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality with a non-admin user fails."""
    token = await register_and_login_default_user(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="test")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="updated")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_update_speciality_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests that updating a non-existent speciality fails."""
    token = await login_user_admin(client)
    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="updated")

    response = await client.put(
        url,
        params={"speciality_id": str(uuid.uuid4())},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Speciality not found"


@pytest.mark.anyio
async def test_update_speciality_to_duplicate_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality to a pre-existing title fails."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)

    spec1 = Speciality(title="title1")
    spec2 = Speciality(title="title2")
    await dao.save(spec1)
    await dao.save(spec2)

    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="title2")

    response = await client.put(
        url,
        params={"speciality_id": str(spec1.id)},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Speciality with this title already exists."


@pytest.mark.anyio
async def test_update_speciality_with_same_title_succeeds(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality with the same title returns 409."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="same_title")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="same_title")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_update_speciality_normalizes_to_lowercase(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality normalizes the title to lowercase."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="original")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("update_speciality_model")
    request = SpecialityRequest(title="UPDATED_TITLE")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "updated_title"

    updated = await dao.find_by_id(speciality.id)
    assert updated.title == "updated_title"


@pytest.mark.anyio
async def test_update_speciality_with_empty_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that updating a speciality with an empty title fails."""
    token = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="test")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("update_speciality_model")

    response = await client.put(
        url,
        params={"speciality_id": str(speciality.id)},
        json={"title": ""},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
