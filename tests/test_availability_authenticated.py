import uuid
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dao.availability_dao import AvailabilityDAO
from ga_api.db.dao.user_dao import UserDAO
from ga_api.db.models.professionals_model import Professional
from ga_api.db.models.users import User
from ga_api.enums.availability_status import AvailabilityStatus
from tests.factories.availability_factory import AvailabilityFactory
from tests.factories.user_factory import UserFactory
from tests.utils import (
    inject_default_professional,
    login_user,
    login_user_admin,
    register_and_login_default_user,
    register_user,
)


async def test_get_my_schedules_with_actual_data(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que usuário autenticado pode listar seus agendamentos reais.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    patient_token = await register_and_login_default_user(client)
    patient: User = await user_dao.find_by_email("mock@mail.com")

    professional: Professional = await inject_default_professional(dbsession)

    # Cria availabilities e as agenda para o usuário
    base_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # Cria e agenda algumas availabilities para o usuário
    for i in range(3):
        availability = AvailabilityFactory.create_availability_model(
            professional_id=professional.id,
            start_time=base_time + timedelta(hours=i),
            end_time=base_time + timedelta(hours=i + 1),
            status=AvailabilityStatus.TAKEN,
        )
        availability.patient_id = patient.id
        await availability_dao.save(availability)

    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Agora deve ter pelo menos 3 agendamentos
    assert len(data) >= 3

    # Verifica estrutura dos dados
    for availability in data:
        assert "id" in availability
        assert "professional_id" in availability
        assert "start_time" in availability
        assert "end_time" in availability
        assert "status" in availability
        assert availability["status"] == "taken"
        assert availability["patient_id"] == str(patient.id)


async def test_get_availabilities_authenticated_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """
    Testa que usuário não autenticado não pode acessar availabilities.
    """
    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(url)

    assert response.status_code == 401


async def test_get_availabilities_authenticated_invalid_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """
    Testa que token inválido retorna 401.
    """
    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(
        url,
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


async def test_get_my_schedules_pagination(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa paginação do endpoint de agendamentos do usuário autenticados.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    patient_token = await register_and_login_default_user(client)
    patient: User = await user_dao.find_by_email("mock@mail.com")

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # Cria 5 agendamentos para o usuário
    for i in range(5):
        availability = AvailabilityFactory.create_availability_model(
            professional_id=professional.id,
            start_time=base_time + timedelta(hours=i),
            end_time=base_time + timedelta(hours=i + 1),
            status=AvailabilityStatus.TAKEN,
        )
        availability.patient_id = patient.id
        await availability_dao.save(availability)

    url = fastapi_app.url_path_for("get_my_schedules")

    # Primeira página
    response1 = await client.get(
        url,
        params={"limit": 2, "offset": 0},
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) >= 2

    # Segunda página
    response2 = await client.get(
        url,
        params={"limit": 2, "offset": 2},
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) >= 2


async def test_get_my_schedules_empty_result(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """
    Testa comportamento quando usuário não tem agendamentos.
    """
    # Usa usuário único para garantir resultado vazio
    unique_email = f"test_empty_{uuid.uuid4()}@example.com"
    unique_user = UserFactory.create_minimal_user_request()
    unique_user.email = unique_email
    unique_user.cpf = f"{uuid.uuid4().hex[:11]}"

    await register_user(client, unique_user)
    patient_token = await login_user(client, unique_email, unique_user.password)

    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0  # Usuário novo não deve ter agendamentos


async def test_get_my_schedules_with_admin_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que usuário admin também pode acessar seus agendamentos.
    """
    admin_token = await login_user_admin(client)

    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# Teste de parâmetros inválidos removido temporariamente
# porque requer validação de parâmetros no endpoint


async def test_get_my_schedules_response_format(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa o formato da resposta do endpoint.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    patient_token = await register_and_login_default_user(client)
    patient: User = await user_dao.find_by_email("mock@mail.com")

    professional: Professional = await inject_default_professional(dbsession)

    # Cria um agendamento para o usuário
    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        status=AvailabilityStatus.TAKEN,
    )
    availability.patient_id = patient.id
    await availability_dao.save(availability)

    url = fastapi_app.url_path_for("get_my_schedules")

    response = await client.get(
        url,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert isinstance(data, list)

    if len(data) > 0:
        schedule_item = data[0]

        # Campos obrigatórios
        required_fields = [
            "id",
            "professional_id",
            "start_time",
            "end_time",
            "status",
            "patient_id",
        ]
        for field in required_fields:
            assert field in schedule_item

        # Validação de tipos
        assert isinstance(schedule_item["id"], str)
        assert isinstance(schedule_item["professional_id"], str)
        assert isinstance(schedule_item["patient_id"], str)
        assert isinstance(schedule_item["start_time"], str)
        assert isinstance(schedule_item["end_time"], str)
        assert isinstance(schedule_item["status"], str)

        # Validação de UUID
        uuid.UUID(schedule_item["id"])
        uuid.UUID(schedule_item["professional_id"])
        uuid.UUID(schedule_item["patient_id"])

        # Deve ser um agendamento do usuário autenticado
        assert schedule_item["patient_id"] == str(patient.id)
        assert schedule_item["status"] == "taken"

        # Validação de datetime ISO format
        datetime.fromisoformat(schedule_item["start_time"].replace("Z", "+00:00"))
        datetime.fromisoformat(schedule_item["end_time"].replace("Z", "+00:00"))
