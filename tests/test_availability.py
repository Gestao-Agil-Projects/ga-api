import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.models.professionals_model import Professional
from ga_api.enums.availability_status import AvailabilityStatus
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest
from tests.factories.availability_factory import AvailabilityFactory
from tests.utils import (
    inject_default_professional,
    login_user_admin,
    register_and_login_default_user,
    save_and_expect,
)

AVAILABILITY_URL = "/api/admin/availability/"
PATIENT_URL = "/api/availability"


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

    professional: Professional = await inject_default_professional(dbsession)

    request: AvailabilityRequest = AvailabilityFactory.create_custom_request(
        start_time=start_time, end_time=end_time, professional_id=professional.id
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

    professional: Professional = await inject_default_professional(dbsession)

    request: AvailabilityRequest = AvailabilityFactory.create_custom_request(
        start_time=start_time, end_time=end_time, professional_id=professional.id
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


@pytest.mark.anyio
async def test_register_availability_overlapping_returns_conflict(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro de uma disponibilidade que sobrepõe outra já existente.
    O resultado esperado é um erro 409 Conflict.
    """
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    base_start_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=2)
    base_end_time = base_start_time + timedelta(hours=1)
    base_request = AvailabilityFactory.create_custom_request(
        start_time=base_start_time,
        end_time=base_end_time,
        professional_id=professional.id,
    )

    response_base: Response = await client.post(
        AVAILABILITY_URL,
        json=base_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response_base.status_code == status.HTTP_200_OK

    # 2. Tenta criar uma nova disponibilidade que sobrepõe a base (ex: das 10:30 às 11:30)
    overlapping_start_time = base_start_time + timedelta(minutes=30)
    overlapping_end_time = overlapping_start_time + timedelta(hours=1)
    overlapping_request = AvailabilityFactory.create_custom_request(
        start_time=overlapping_start_time,
        end_time=overlapping_end_time,
        professional_id=professional.id,
    )

    response_overlap: Response = await client.post(
        AVAILABILITY_URL,
        json=overlapping_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response_overlap.status_code == status.HTTP_409_CONFLICT
    assert (
        response_overlap.json()["detail"]
        == "time interval is conflicting with existent availability"
    )


@pytest.mark.anyio
async def test_register_availability_as_admin_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro de uma nova disponibilidade por um usuário administrador.
    O fluxo deve ser bem-sucedido.
    """
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    request: AvailabilityRequest = AvailabilityFactory.create_default_request(
        professional_id=professional.id
    )

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert "id" in body
    assert str(body["professional_id"]) == str(request.professional_id)
    assert body["start_time"].replace("Z", "+00:00") == request.start_time.isoformat()
    assert body["end_time"].replace("Z", "+00:00") == request.end_time.isoformat()


@pytest.mark.anyio
async def test_register_availability_as_admin_professional_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa o registro de uma nova disponibilidade por um usuário administrador.
    O fluxo deve dar erro ao não encontrar o profissional.
    """
    admin_token: str = await login_user_admin(client)

    request: AvailabilityRequest = AvailabilityFactory.create_default_request(
        professional_id=uuid.uuid4()
    )

    response: Response = await client.post(
        AVAILABILITY_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_availability_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de atualização de disponibilidade sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    dao = AvailabilityDAO(dbsession)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    payload = {"status": AvailabilityStatus.TAKEN}

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_availability_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de atualização de disponibilidade sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    dao = AvailabilityDAO(dbsession)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    payload = {"status": AvailabilityStatus.TAKEN.value}

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_availability_as_patient_returns_forbidden(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de atualização de disponibilidade por um usuário não-administrador.
    O resultado esperado é um erro 403 Forbidden.
    """
    dao = AvailabilityDAO(dbsession)
    patient_token: str = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    payload = {"status": AvailabilityStatus.TAKEN.value}

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User does not have admin privileges"


@pytest.mark.anyio
async def test_update_availability_with_nonexistent_id_returns_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de uma disponibilidade com um UUID que não existe no banco de dados.
    O resultado esperado é um erro 404 Not Found.
    """
    admin_token: str = await login_user_admin(client)
    non_existent_id = uuid.uuid4()
    payload = {"status": AvailabilityStatus.TAKEN.value}

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{non_existent_id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Availability not found"


@pytest.mark.anyio
async def test_update_availability_with_empty_payload_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com payload vazio (nenhum campo fornecido).
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "At least one field must be provided"


@pytest.mark.anyio
async def test_update_availability_with_only_start_time_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização fornecendo apenas start_time sem end_time.
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    payload = {
        "start_time": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "start_time and end_time must both be provided or both omitted"
    )


@pytest.mark.anyio
async def test_update_availability_with_only_end_time_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização fornecendo apenas end_time sem start_time.
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    payload = {
        "end_time": (
            datetime.now(timezone.utc) + timedelta(days=5, hours=1)
        ).isoformat()
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "start_time and end_time must both be provided or both omitted"
    )


@pytest.mark.anyio
async def test_update_availability_with_start_time_after_end_time_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com start_time maior que end_time.
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    start_time = datetime.now(timezone.utc) + timedelta(days=3)
    end_time = start_time - timedelta(minutes=30)
    payload = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid time interval"


@pytest.mark.anyio
async def test_update_availability_with_equal_start_and_end_times_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com start_time igual a end_time.
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    same_time = datetime.now(timezone.utc) + timedelta(days=3)
    payload = {
        "start_time": same_time.isoformat(),
        "end_time": same_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid time interval"


@pytest.mark.anyio
async def test_update_availability_longer_than_two_hours_returns_bad_request(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com intervalo de tempo maior que 2 horas.
    O resultado esperado é um erro 400 Bad Request.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    start_time = datetime.now(timezone.utc) + timedelta(days=4)
    end_time = start_time + timedelta(hours=2, minutes=1)
    payload = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "Maximum time interval between start and end must be 2 hours"
    )


@pytest.mark.anyio
async def test_update_availability_exactly_two_hours_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com intervalo de exatamente 2 horas (limite válido).
    O resultado esperado é sucesso.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    start_time = datetime.now(timezone.utc) + timedelta(days=4)
    end_time = start_time + timedelta(hours=2)
    payload = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_update_availability_overlapping_another_returns_conflict(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de uma availability que causaria sobreposição com outra existente.
    O resultado esperado é um erro 409 Conflict.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    # Cria duas availabilities não conflitantes
    start_time_a = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=10)
    availability_a = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=start_time_a,
        end_time=start_time_a + timedelta(hours=1),  # 10:00 - 11:00
    )

    start_time_b = start_time_a + timedelta(hours=2)  # 12:00
    availability_b = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=start_time_b,
        end_time=start_time_b + timedelta(hours=1),  # 12:00 - 13:00
    )

    await save_and_expect(dao, [availability_a, availability_b], 2)

    # Tenta atualizar a availability A para sobrepor a B (12:30 - 13:30)
    payload = {
        "start_time": (start_time_b + timedelta(minutes=30)).isoformat(),
        "end_time": (start_time_b + timedelta(hours=1, minutes=30)).isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability_a.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json()["detail"]
        == "time interval is conflicting with existent availability"
    )


@pytest.mark.anyio
async def test_update_availability_overlapping_start_of_another_returns_conflict(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização que sobrepõe o início de outra availability.
    O resultado esperado é um erro 409 Conflict.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=14, minute=0, second=0, microsecond=0
    ) + timedelta(days=15)

    # Availability A: 14:00 - 15:00
    availability_A = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
    )

    # Availability B: 16:00 - 17:00
    availability_B = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time + timedelta(hours=2),
        end_time=base_time + timedelta(hours=3),
    )

    await save_and_expect(dao, [availability_A, availability_B], 2)

    # Tenta atualizar B para 13:30 - 14:30 (sobrepõe o início de A)
    payload = {
        "start_time": (base_time - timedelta(minutes=30)).isoformat(),
        "end_time": (base_time + timedelta(minutes=30)).isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability_B.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json()["detail"]
        == "time interval is conflicting with existent availability"
    )


@pytest.mark.anyio
async def test_update_availability_overlapping_end_of_another_returns_conflict(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização que sobrepõe o final de outra availability.
    O resultado esperado é um erro 409 Conflict.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=9, minute=0, second=0, microsecond=0
    ) + timedelta(days=20)

    # Availability A: 09:00 - 10:00
    availability_A = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
    )

    # Availability B: 11:00 - 12:00
    availability_B = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time + timedelta(hours=2),
        end_time=base_time + timedelta(hours=3),
    )

    await save_and_expect(dao, [availability_A, availability_B], 2)

    # Tenta atualizar B para 09:30 - 10:30 (sobrepõe o final de A)
    payload = {
        "start_time": (base_time + timedelta(minutes=30)).isoformat(),
        "end_time": (base_time + timedelta(hours=1, minutes=30)).isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability_B.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json()["detail"]
        == "time interval is conflicting with existent availability"
    )


@pytest.mark.anyio
async def test_update_availability_completely_contains_another_returns_conflict(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização onde o novo intervalo contém completamente outra availability.
    O resultado esperado é um erro 409 Conflict.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=13, minute=0, second=0, microsecond=0
    ) + timedelta(days=25)

    # Availability A: 14:00 - 16:00
    availability_A = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time + timedelta(hours=1),
        end_time=base_time + timedelta(hours=2),
    )

    # Availability B: 16:00 - 17:00
    availability_B = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time + timedelta(hours=3),
        end_time=base_time + timedelta(hours=4),
    )

    await save_and_expect(dao, [availability_A, availability_B], 2)

    # Tenta atualizar B para 14:00 - 15:00 (contem o horario de A)
    payload = {
        "start_time": (base_time + timedelta(hours=1)).isoformat(),
        "end_time": (base_time + timedelta(hours=2)).isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability_B.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json()["detail"]
        == "time interval is conflicting with existent availability"
    )


@pytest.mark.anyio
async def test_update_availability_to_adjacent_time_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização para um horário adjacente (end_time de uma == start_time de outra).
    Não deve gerar conflito. O resultado esperado é sucesso.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=8, minute=0, second=0, microsecond=0
    ) + timedelta(days=30)

    # Availability A: 08:00 - 09:00
    availability_A = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
    )

    # Availability B: 10:00 - 11:00
    availability_B = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=base_time + timedelta(hours=2),
        end_time=base_time + timedelta(hours=3),
    )

    await save_and_expect(dao, [availability_A, availability_B], 2)

    # Atualiza B para 09:00 - 10:00 (adjacente a A, sem sobreposição)
    payload = {
        "start_time": (base_time + timedelta(hours=1)).isoformat(),
        "end_time": (base_time + timedelta(hours=2)).isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability_B.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_update_availability_to_same_time_interval_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa que é possível atualizar uma availability mantendo o mesmo intervalo de tempo
    (não deve gerar conflito consigo mesma).
    O fluxo deve ser bem-sucedido.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    start_time = datetime.now(timezone.utc) + timedelta(days=4, hours=15)
    end_time = start_time + timedelta(hours=1)

    availability = AvailabilityFactory.create_availability_model(
        professional.id,
        start_time=start_time,
        end_time=end_time,
        status=AvailabilityStatus.AVAILABLE,
    )
    await save_and_expect(dao, availability, 1)

    # Atualiza mantendo os mesmos horários mas mudando o status
    payload = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": AvailabilityStatus.TAKEN.value,
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(availability.id)
    assert body["status"] == AvailabilityStatus.TAKEN.value


@pytest.mark.anyio
async def test_update_availability_only_status_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização bem-sucedida de apenas o status de uma availability.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(
        professional.id, status=AvailabilityStatus.AVAILABLE
    )
    await save_and_expect(dao, availability, 1)

    original_start_time = availability.start_time
    original_end_time = availability.end_time

    payload = {"status": AvailabilityStatus.TAKEN.value}

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == AvailabilityStatus.TAKEN.value
    # Verifica que os horários não foram alterados
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == original_start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == original_end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_update_availability_only_times_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização bem-sucedida de apenas o horário (start e end time) de uma availability.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(
        professional.id, status=AvailabilityStatus.AVAILABLE
    )
    await save_and_expect(dao, availability, 1)

    original_status = availability.status

    new_start_time = datetime.now(timezone.utc) + timedelta(days=6)
    new_end_time = new_start_time + timedelta(hours=1, minutes=30)

    payload = {
        "start_time": new_start_time.isoformat(),
        "end_time": new_end_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == original_status.value  # Status original mantido
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == new_start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == new_end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_update_availability_all_fields_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização bem-sucedida de todos os campos permitidos (horário e status).
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(
        professional.id, status=AvailabilityStatus.AVAILABLE
    )
    await save_and_expect(dao, availability, 1)

    new_start_time = datetime.now(timezone.utc) + timedelta(days=7)
    new_end_time = new_start_time + timedelta(minutes=45)
    new_status = AvailabilityStatus.CANCELED

    payload = {
        "start_time": new_start_time.isoformat(),
        "end_time": new_end_time.isoformat(),
        "status": new_status.value,
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == new_status.value
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == new_start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == new_end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_update_availability_with_very_short_interval_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com um intervalo muito curto (ex: 15 minutos).
    O resultado esperado é sucesso.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(professional.id)
    await save_and_expect(dao, availability, 1)

    new_start_time = datetime.now(timezone.utc) + timedelta(days=8)
    new_end_time = new_start_time + timedelta(minutes=15)

    payload = {
        "start_time": new_start_time.isoformat(),
        "end_time": new_end_time.isoformat(),
    }

    response: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == new_start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == new_end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_update_availability_multiple_times_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa múltiplas atualizações sequenciais da mesma availability.
    Todas devem ser bem-sucedidas.
    """
    dao = AvailabilityDAO(dbsession)
    admin_token: str = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)
    availability = AvailabilityFactory.create_availability_model(
        professional.id, status=AvailabilityStatus.AVAILABLE
    )
    await save_and_expect(dao, availability, 1)

    # Primeira atualização: muda apenas o status
    response1: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json={"status": AvailabilityStatus.TAKEN.value},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response1.status_code == status.HTTP_200_OK
    assert response1.json()["status"] == AvailabilityStatus.TAKEN.value

    # Segunda atualização: muda os horários
    new_start_time = datetime.now(timezone.utc) + timedelta(days=12)
    new_end_time = new_start_time + timedelta(hours=1)
    response2: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json={
            "start_time": new_start_time.isoformat(),
            "end_time": new_end_time.isoformat(),
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response2.status_code == status.HTTP_200_OK
    assert datetime.fromisoformat(response2.json()["start_time"]).replace(
        tzinfo=None
    ) == new_start_time.replace(tzinfo=None)

    # Terceira atualização: muda tudo
    newer_start_time = datetime.now(timezone.utc) + timedelta(days=15)
    newer_end_time = newer_start_time + timedelta(minutes=30)
    response3: Response = await client.put(
        f"{AVAILABILITY_URL}{availability.id}",
        json={
            "start_time": newer_start_time.isoformat(),
            "end_time": newer_end_time.isoformat(),
            "status": AvailabilityStatus.CANCELED.value,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response3.status_code == status.HTTP_200_OK
    body = response3.json()
    assert body["status"] == AvailabilityStatus.CANCELED.value
    assert datetime.fromisoformat(body["start_time"]).replace(
        tzinfo=None
    ) == newer_start_time.replace(tzinfo=None)
    assert datetime.fromisoformat(body["end_time"]).replace(
        tzinfo=None
    ) == newer_end_time.replace(tzinfo=None)


@pytest.mark.anyio
async def test_get_availabilities_admin_returns_all(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    admin_token = await login_user_admin(client)
    professional: Professional = await inject_default_professional(dbsession)
    dao = AvailabilityDAO(dbsession)

    now = datetime.now(timezone.utc)
    availabilities = [
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now - timedelta(days=2),
            end_time=now - timedelta(days=1),
            status=AvailabilityStatus.TAKEN,
        ),
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            status=AvailabilityStatus.AVAILABLE,
        ),
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
            status=AvailabilityStatus.CANCELED,
        ),
    ]
    await save_and_expect(dao, availabilities, 3)

    response = await client.get(
        f"{AVAILABILITY_URL}?professional_id={professional.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    returned_ids = {item["id"] for item in data}
    for availability in availabilities:
        assert str(availability.id) in returned_ids


@pytest.mark.anyio
async def test_get_availabilities_patient_returns_only_available_future(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    patient_token = await register_and_login_default_user(client)
    professional: Professional = await inject_default_professional(dbsession)
    dao = AvailabilityDAO(dbsession)

    now = datetime.now(timezone.utc)
    availabilities = [
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now - timedelta(days=2),
            end_time=now - timedelta(days=1),
            status=AvailabilityStatus.AVAILABLE,
        ),
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            status=AvailabilityStatus.AVAILABLE,
        ),
        AvailabilityFactory.create_availability_model(
            professional.id,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
            status=AvailabilityStatus.TAKEN,
        ),
    ]
    await save_and_expect(dao, availabilities, 3)

    response = await client.get(
        f"{PATIENT_URL}/?professional_id={professional.id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == AvailabilityStatus.AVAILABLE.value
    assert datetime.fromisoformat(data[0]["start_time"]).replace(
        tzinfo=None
    ) > now.replace(tzinfo=None)
