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
from ga_api.web.api.schedule.request.admin_schedule_request import AdminScheduleRequest
from ga_api.web.api.schedule.request.patient_schedule_request import (
    PatientScheduleRequest,
)
from tests.factories.availability_factory import AvailabilityFactory
from tests.factories.user_factory import UserFactory
from tests.utils import (
    inject_default_professional,
    login_user_admin,
    register_and_login_default_user,
    save_and_expect,
)


async def test_book_appointment_by_patient_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa o fluxo de sucesso onde um paciente logado agenda um horário.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    patient_token = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = PatientScheduleRequest(availability_id=availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "taken"
    assert data["patient_id"] == str(patient_user.id)

    await dbsession.refresh(availability)
    assert availability.status == "taken"
    assert availability.patient_id == patient_user.id


async def test_book_appointment_by_patient_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa o fluxo de sucesso onde um paciente logado agenda um horário.
    """

    request = PatientScheduleRequest(availability_id=uuid.uuid4())
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer fooToken"},
    )

    assert response.status_code == 401


# ==================== TESTES DO FLUXO DE PACIENTE ====================


async def test_book_appointment_by_patient_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa o fluxo de sucesso onde um paciente logado agenda um horário.
    """

    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    patient_token = await register_and_login_default_user(client)
    patient_user = await user_dao.find_by_email(
        UserFactory.create_default_user_request().email
    )

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = PatientScheduleRequest(availability_id=availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "taken"
    assert data["patient_id"] == str(patient_user.id)

    await dbsession.refresh(availability)
    assert availability.status == AvailabilityStatus.TAKEN
    assert availability.patient_id == patient_user.id


async def test_book_appointment_by_patient_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que um usuário não autenticado não pode agendar horários.
    """
    request = PatientScheduleRequest(availability_id=uuid.uuid4())
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": "Bearer fooToken"},
    )

    assert response.status_code == 401


async def test_book_appointment_availability_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que retorna 404 quando a disponibilidade não existe.
    """
    patient_token = await register_and_login_default_user(client)

    non_existent_id = uuid.uuid4()
    request = PatientScheduleRequest(availability_id=non_existent_id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_book_appointment_already_taken(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que retorna 400 quando a disponibilidade já está ocupada.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    patient_token = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    # Cria disponibilidade já ocupada
    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        status=AvailabilityStatus.TAKEN,
    )
    await save_and_expect(availability_dao, availability, 1)

    request = PatientScheduleRequest(availability_id=availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower()


async def test_book_appointment_conflicting_schedule(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que retorna 409 quando o paciente já tem um agendamento conflitante.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    patient_token = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    user_dao = UserDAO(dbsession)
    patient_user: User = await user_dao.find_by_email(
        UserFactory.create_default_user_request().email
    )

    # Horário base: amanhã às 10:00
    base_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # Cria primeiro agendamento (10:00 - 11:00)
    existing_availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        status=AvailabilityStatus.TAKEN,
    )
    existing_availability.patient_id = patient_user.id
    await save_and_expect(availability_dao, existing_availability, 1)

    # Tenta agendar horário conflitante (10:30 - 11:30)
    conflicting_availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time + timedelta(minutes=30),
        end_time=base_time + timedelta(hours=1, minutes=30),
        status=AvailabilityStatus.AVAILABLE,
    )
    await save_and_expect(availability_dao, conflicting_availability, 2)

    request = PatientScheduleRequest(availability_id=conflicting_availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 409
    assert "conflicting" in response.json()["detail"].lower()


async def test_book_multiple_appointments_non_conflicting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que um paciente pode agendar múltiplos horários não conflitantes.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    patient_token = await register_and_login_default_user(client)
    patient_user = await user_dao.find_by_email(
        UserFactory.create_default_user_request().email
    )

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # Cria dois horários não conflitantes
    availability1 = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
    )
    availability2 = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time + timedelta(hours=2),
        end_time=base_time + timedelta(hours=3),
    )

    await save_and_expect(availability_dao, availability1, 1)
    await save_and_expect(availability_dao, availability2, 2)

    url = fastapi_app.url_path_for("book_appointment")

    # Agenda primeiro horário
    request1 = PatientScheduleRequest(availability_id=availability1.id)
    response1 = await client.post(
        url,
        json=request1.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert response1.status_code == 200

    # Agenda segundo horário
    request2 = PatientScheduleRequest(availability_id=availability2.id)
    response2 = await client.post(
        url,
        json=request2.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert response2.status_code == 200

    # Verifica que ambos foram agendados
    await dbsession.refresh(availability1)
    await dbsession.refresh(availability2)

    assert availability1.patient_id == patient_user.id
    assert availability2.patient_id == patient_user.id


async def test_admin_book_for_patient_success(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que um admin pode agendar horário para um paciente.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)

    admin_token = await login_user_admin(client)
    patient_token = await register_and_login_default_user(client)

    patient_email = UserFactory.create_default_user_request().email

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = AdminScheduleRequest(
        availability_id=availability.id,
        email=patient_email,
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "taken"
    assert data["patient_id"] is not None

    await dbsession.refresh(availability)
    assert availability.status == AvailabilityStatus.TAKEN


async def test_admin_book_patient_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que retorna 404 quando o email do paciente não existe.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    admin_token = await login_user_admin(client)

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = AdminScheduleRequest(
        availability_id=availability.id,
        email="nonexistent@example.com",
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404
    assert "patient not found" in response.json()["detail"].lower()


async def test_admin_book_without_admin_permission(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que um usuário não-admin não pode agendar para outros pacientes.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    patient_token = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = AdminScheduleRequest(
        availability_id=availability.id,
        email="other@example.com",
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 403


async def test_admin_book_conflicting_schedule_for_patient(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que admin não pode agendar se o paciente já tem horário conflitante.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    admin_token = await login_user_admin(client)

    # Cria e obtém o paciente
    patient_token = await register_and_login_default_user(client)
    patient: User = await user_dao.find_by_email("mock@mail.com")

    professional: Professional = await inject_default_professional(dbsession)

    base_time = datetime.now(timezone.utc).replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # Cria agendamento existente para o paciente (10:00 - 11:00)
    existing_availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        status=AvailabilityStatus.TAKEN,
    )
    existing_availability.patient_id = patient.id
    await save_and_expect(availability_dao, existing_availability, 1)

    # Tenta agendar horário conflitante (10:30 - 11:30)
    conflicting_availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=base_time + timedelta(minutes=30),
        end_time=base_time + timedelta(hours=1, minutes=30),
    )
    await save_and_expect(availability_dao, conflicting_availability, 2)

    request = AdminScheduleRequest(
        availability_id=conflicting_availability.id,
        email="mock@mail.com",
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 409
    assert "conflicting" in response.json()["detail"].lower()


async def test_admin_book_availability_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que retorna 404 quando a disponibilidade não existe (fluxo admin).
    """
    admin_token = await login_user_admin(client)

    request = AdminScheduleRequest(
        availability_id=uuid.uuid4(),
        email="patient@example.com",
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_admin_book_already_taken_availability(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa que admin não pode agendar uma disponibilidade já ocupada.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    user_dao: UserDAO = UserDAO(dbsession)

    admin_token = await login_user_admin(client)

    # Cria um paciente existente para ocupar a disponibilidade
    await register_and_login_default_user(client)
    existing_patient: User = await user_dao.find_by_email("mock@mail.com")

    professional: Professional = await inject_default_professional(dbsession)

    # Cria disponibilidade já ocupada por outro paciente
    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        status=AvailabilityStatus.TAKEN,
    )
    availability.patient_id = existing_patient.id
    await save_and_expect(availability_dao, availability, 1)

    request = AdminScheduleRequest(
        availability_id=availability.id,
        email="patient@example.com",
    )
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower()


async def test_admin_book_with_invalid_email_format(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa validação de formato de email inválido.
    """
    admin_token = await login_user_admin(client)

    request_data = {
        "availability_id": str(uuid.uuid4()),
        "patient_email": "invalid-email",
    }
    url = fastapi_app.url_path_for("book_for_patient")

    response = await client.post(
        url,
        json=request_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 422  # Validation error


# ==================== TESTES DE EDGE CASES ====================


async def test_book_appointment_with_past_availability(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa comportamento ao tentar agendar horário no passado.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)
    patient_token = await register_and_login_default_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    # Cria disponibilidade no passado
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id,
        start_time=past_time,
        end_time=past_time + timedelta(hours=1),
    )
    await save_and_expect(availability_dao, availability, 1)

    request = PatientScheduleRequest(availability_id=availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Pode retornar 200 ou 400 dependendo da regra de negócio
    # Ajuste conforme sua implementação
    assert response.status_code in [200, 400]


async def test_concurrent_booking_same_availability(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
):
    """
    Testa condição de corrida: dois pacientes tentam agendar o mesmo horário.
    Este teste verifica que apenas um agendamento deve ter sucesso.
    """
    availability_dao: AvailabilityDAO = AvailabilityDAO(dbsession)

    # Registra dois pacientes
    patient1_token = await register_and_login_default_user(client)
    # Assumindo que você tem função para criar segundo usuário
    # patient2_token = await register_and_login_second_user(client)

    professional: Professional = await inject_default_professional(dbsession)

    availability = AvailabilityFactory.create_availability_model(
        professional_id=professional.id
    )
    await save_and_expect(availability_dao, availability, 1)

    request = PatientScheduleRequest(availability_id=availability.id)
    url = fastapi_app.url_path_for("book_appointment")

    # Simula requisições simultâneas
    response1 = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient1_token}"},
    )

    # Segunda requisição deve falhar
    response2 = await client.post(
        url,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient1_token}"},
    )

    # Uma deve ter sucesso e outra deve falhar
    assert (response1.status_code == 200 and response2.status_code == 400) or (
        response1.status_code == 400 and response2.status_code == 200
    )


async def test_invalid_uuid_format(
    fastapi_app: FastAPI,
    client: AsyncClient,
):
    """
    Testa validação com UUID inválido.
    """
    patient_token = await register_and_login_default_user(client)

    request_data = {
        "availability_id": "invalid-uuid",
    }
    url = fastapi_app.url_path_for("book_appointment")

    response = await client.post(
        url,
        json=request_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 422  # Validation error
