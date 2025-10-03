import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.professional_factories import (
    ProfessionalFactory,
    AvailabilityFactory,
)
from ga_api.db.models.users import User
from ga_api.db.models.availability_model import Availability

pytestmark = pytest.mark.anyio


async def test_book_appointment_by_patient_success(
    authenticated_patient_client: AsyncClient,  # Paciente
    patient_user: User,  # User do paciente
    dbsession: AsyncSession,  # Conexao com o Banco
):
    """
    Testa o fluxo de sucesso onde um paciente logado agenda um horário.
    """
    professional = ProfessionalFactory.create_db_model()
    dbsession.add(professional)
    await dbsession.flush()

    availability = AvailabilityFactory.create_db_model(professional_id=professional.id)
    dbsession.add(availability)
    await dbsession.commit()

    request_body = {"availability_id": str(availability.id)}
    response = await authenticated_patient_client.post(
        "/api/scheduling/schedule", json=request_body
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "taken"
    assert data["patient_id"] == str(patient_user.id)

    await dbsession.refresh(availability)
    assert availability.status == "taken"
    assert availability.patient_id == patient_user.id
