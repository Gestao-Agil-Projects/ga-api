import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, Response
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.web.api.availability.request.availability_request import AvailabilityRequest
from tests.factories.availability_factory import AvailabilityFactory
from tests.utils import login_user_admin, register_and_login_default_user

AVAILABILITY_URL = "/api/admin/availability/"


@pytest.mark.anyio
async def test_register_availability_as_patient_returns_forbidden(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de registro de disponibilidade por um usuário não-administrador (paciente).
    O resultado esperado é um erro 403 Forbidden.
    """
    patient_token: str = await register_and_login_default_user(client)
    request: AvailabilityRequest = AvailabilityFactory.create_default_request()

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User does not have admin privileges"


@pytest.mark.anyio
async def test_register_availability_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de registro de disponibilidade sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    request: AvailabilityRequest = AvailabilityFactory.create_default_request()

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_register_availability_with_start_time_after_end_time_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro com start_time maior que end_time.
    O resultado esperado é um erro 400 Bad Request.
    """
    admin_token: str = await login_user_admin(client)
    start_time = datetime.now(timezone.utc) + timedelta(days=1, hours=1)
    end_time = start_time - timedelta(minutes=30)
    request: AvailabilityRequest = AvailabilityFactory.create_custom_request(
        start_time=start_time, end_time=end_time
    )

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid time interval"


@pytest.mark.anyio
async def test_register_availability_longer_than_two_hours_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro de uma disponibilidade com duração maior que 2 horas.
    O resultado esperado é um erro 400 Bad Request.
    """
    admin_token: str = await login_user_admin(client)
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=2, minutes=1)
    request: AvailabilityRequest = AvailabilityFactory.create_custom_request(
        start_time=start_time, end_time=end_time
    )

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "Maximum time interval between start and end must be 2 hours"
    )


@pytest.mark.anyio
async def test_register_availability_without_start_time_returns_unprocessable_entity(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro de disponibilidade sem um campo obrigatório (start_time).
    O resultado esperado é um erro 422 Unprocessable Entity.
    """
    admin_token: str = await login_user_admin(client)
    request: AvailabilityRequest = AvailabilityFactory.create_default_request()

    request_data = request.model_dump(mode="json")
    del request_data["start_time"]

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert "start_time" in str(body)
    assert "Field required" in str(body)


# ESTES TESTES SERÃO REATIVADOS APÓS A DEMANDA DO CADASTRO DE PROFISSIONAL
#
# @pytest.mark.anyio
# async def test_register_availability_overlapping_returns_conflict(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
# ) -> None:
#     """
#     Testa o registro de uma disponibilidade que sobrepõe outra já existente.
#     O resultado esperado é um erro 409 Conflict.
#     """
#     admin_token: str = await login_user_admin(client)
#
#     base_start_time = datetime.now(timezone.utc).replace(
#         hour=10, minute=0, second=0, microsecond=0
#     ) + timedelta(days=2)
#     base_end_time = base_start_time + timedelta(hours=1)
#     base_request = AvailabilityFactory.create_custom_request(
#         start_time=base_start_time, end_time=base_end_time
#     )
#
#     response_base: Response = await client.post(
#         AVAILABILITY_URL,
#         json=base_request.model_dump(mode="json"),
#         headers={"Authorization": f"Bearer {admin_token}"},
#     )
#     assert response_base.status_code == status.HTTP_200_OK
#
#     # 2. Tenta criar uma nova disponibilidade que sobrepõe a base (ex: das 10:30 às 11:30)
#     overlapping_start_time = base_start_time + timedelta(minutes=30)
#     overlapping_end_time = overlapping_start_time + timedelta(hours=1)
#     overlapping_request = AvailabilityFactory.create_custom_request(
#         start_time=overlapping_start_time, end_time=overlapping_end_time
#     )
#
#     response_overlap: Response = await client.post(
#         AVAILABILITY_URL,
#         json=overlapping_request.model_dump(mode="json"),
#         headers={"Authorization": f"Bearer {admin_token}"},
#     )
#
#     assert response_overlap.status_code == status.HTTP_409_CONFLICT
#     assert (
#         response_overlap.json()["detail"]
#         == "time interval is conflicting with existent availability"
#     )

#
# @pytest.mark.anyio
# async def test_register_availability_as_admin_success(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
# ) -> None:
#     """
#     Testa o registro de uma nova disponibilidade por um usuário administrador.
#     O fluxo deve ser bem-sucedido.
#     """
#     admin_token: str = await login_user_admin(client)
#     request: AvailabilityRequest = AvailabilityFactory.create_default_request()
#
#     response: Response = await client.post(
#         AVAILABILITY_URL,
#         json=request.model_dump(mode="json"),
#         headers={"Authorization": f"Bearer {admin_token}"},
#     )
#
#     assert response.status_code == status.HTTP_200_OK
#     body = response.json()
#
#     assert "id" in body
#     assert "created_by_id" in body
#     assert body["professional_id"] == request.professional_id
#     assert body["start_time"].replace("Z", "+00:00") == request.start_time.isoformat()
#     assert body["end_time"].replace("Z", "+00:00") == request.end_time.isoformat()
