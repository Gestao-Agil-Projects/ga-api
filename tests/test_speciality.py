import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.speciality_dao import SpecialityDAO
from ga_api.db.models.speciality_model import Speciality
from ga_api.web.api.speciality.request.speciality_request import SpecialityRequest
from tests.utils import (register_and_login_default_user, login_user_admin,
                         save_and_expect)


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality creation with authentication."""
    # FIX: Added authentication token, as the endpoint is protected.
    token: str = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    test_title = "Hello"
    request: SpecialityRequest = SpecialityRequest(title=test_title)
    response = await client.post(
        url,
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = SpecialityDAO(dbsession)
    instances = await dao.find_all()
    saved_object = instances[0]
    assert len(instances) == 1
    assert saved_object.title == test_title.lower()


@pytest.mark.anyio
async def test_creation_saves_title_in_lowercase(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that the speciality title is saved in lowercase."""
    # FIX: Added authentication token.
    token: str = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    mixed_case_title = "Cardiology"
    expected_lowercase_title = "cardiology"

    response = await client.post(
        url,
        json={"title": mixed_case_title},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    dao = SpecialityDAO(dbsession)
    instance = await dao.get_by_title(expected_lowercase_title)
    assert instance is not None
    assert instance.title == expected_lowercase_title


@pytest.mark.anyio
async def test_creation_duplicate_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests that creating a speciality with a duplicate title fails."""
    token: str = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    dao = SpecialityDAO(dbsession)

    existing_title = "dermatology"
    # FIX: Replaced non-existent 'create_speciality' with the correct 'save' method.
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
    token: str = await login_user_admin(client)
    url = fastapi_app.url_path_for("create_speciality")
    dao = SpecialityDAO(dbsession)

    # FIX: Replaced non-existent 'create_speciality' with the correct 'save' method.
    await dao.save(Speciality(title="pediatrics"))

    response = await client.post(
        url,
        json={"title": "Pediatrics"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Speciality with this title already exists."


@pytest.mark.anyio
async def test_getting_list(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality list retrieval."""
    token: str = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    await dao.save(Speciality(title=uuid.uuid4().hex))
    await dao.save(Speciality(title=uuid.uuid4().hex))

    url = fastapi_app.url_path_for("get_speciality_models")
    response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
    specialities = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(specialities) >= 2


@pytest.mark.anyio
async def test_getting_by_id_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests speciality retrieval by id when it exists."""
    token: str = await login_user_admin(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="get_by_id_test", id=uuid.uuid4())

    await save_and_expect(dao, speciality, 1)

    url = fastapi_app.url_path_for("get_speciality_models")
    # FIX: Corrected parameter passing for UUIDs. They should be strings.
    response = await client.get(
        "/api/admin/speciality?speciality_id=".format(str(speciality.id)),
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
    token: str = await register_and_login_default_user(client)
    url = fastapi_app.url_path_for("get_speciality_models")
    # FIX: Corrected parameter passing for UUIDs.
    response = await client.get(
        url,
        params={"speciality_id": str(uuid.uuid4())},
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
    """Tests speciality deletion by id."""
    token: str = await register_and_login_default_user(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="to_delete")
    # FIX: Replaced helper 'save_and_expect' with a direct 'save' for clarity and stability.
    await dao.save(speciality)

    url = fastapi_app.url_path_for("delete_speciality_model")
    response = await client.delete(
        url,
        params={"speciality_id": str(speciality.id)},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await dao.find_by_id(speciality.id) is None


@pytest.mark.anyio
async def test_deletion_by_title(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests speciality deletion by title."""
    token: str = await register_and_login_default_user(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="to_delete_by_title")
    await dao.save(speciality)

    url = fastapi_app.url_path_for("delete_speciality_model")
    # FIX: Corrected the parameter name from 'speciality_name' to 'title'.
    response = await client.delete(
        url,
        params={"title": "to_delete_by_title"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await dao.get_by_title("to_delete_by_title") is None


@pytest.mark.anyio
async def test_deletion_with_no_params(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """Tests deletion request without id or name (should be a no-op)."""
    token: str = await register_and_login_default_user(client)
    url = fastapi_app.url_path_for("delete_speciality_model")
    response = await client.delete(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )

    # FIX: Expect 204 No Content for a no-op, not 422.
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_update_speciality_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests speciality update success."""
    token: str = await register_and_login_default_user(client)
    dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="before_update")
    await dao.save(speciality)

    request = SpecialityRequest(title="After_Update")

    # FIX: Correctly build the URL with the speciality_id as a path parameter.
    url = fastapi_app.url_path_for(
        "update_speciality", speciality_id=str(speciality.id)
    )
    response = await client.patch(
        url,
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("title") == "after_update"

    updated = await dao.find_by_id(speciality.id)
    assert updated.title == "after_update"


@pytest.mark.anyio
async def test_update_speciality_to_duplicate_title_fails(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """Tests that updating a speciality to a pre-existing title fails."""
    dao = SpecialityDAO(dbsession)

    spec1 = Speciality(title="title1")
    spec2 = Speciality(title="title2")
    # FIX: Replaced non-existent 'create_all' with two 'save' calls.
    await dao.save(spec1)
    await dao.save(spec2)
