import uuid
import pytest
from httpx import AsyncClient, Response
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ga_api.db.dao.speciality_dao import SpecialityDAO
from tests.factories.professional_factory import ProfessionalFactory
from tests.utils import (
    login_user_admin,
    register_and_login_default_user,
    save_and_expect,
)

ADMIN_PROFESSIONAL_URL = "/api/admin/professionals/"
PUBLIC_PROFESSIONAL_URL = "/api/professionals/"


# ==================== CREATE PROFESSIONAL TESTS ====================


@pytest.mark.anyio
async def test_create_professional_as_admin_returns_created(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de um profissional por um usuário administrador.
    O resultado esperado é um status 201 Created.
    """
    admin_token: str = await login_user_admin(client)
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. João Silva",
        bio="Especialista em cardiologia",
        phone="+5551999999999",
        email="joao.silva@example.com",
        is_enabled=True,
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["full_name"] == "Dr. João Silva"
    assert body["bio"] == "Especialista em cardiologia"
    assert "id" in body


@pytest.mark.anyio
async def test_create_professional_as_patient_returns_forbidden(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de criação de profissional por um usuário não-administrador.
    O resultado esperado é um erro 403 Forbidden.
    """
    patient_token: str = await register_and_login_default_user(client)
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Maria Santos",
        bio="Dermatologista",
        phone="+5551988888888",
        email="maria.santos@example.com",
        is_enabled=True,
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User does not have admin privileges"


@pytest.mark.anyio
async def test_create_professional_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de criação de profissional sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Pedro Oliveira",
        bio="Ortopedista",
        phone="+5551977777777",
        email="pedro.oliveira@example.com",
        is_enabled=True,
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_create_professional_without_full_name_returns_unprocessable_entity(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de profissional sem campo obrigatório (full_name).
    O resultado esperado é um erro 422 Unprocessable Entity.
    """
    admin_token: str = await login_user_admin(client)
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Ana Costa",
        bio="Neurologista",
        phone="+5551966666666",
        email="ana.costa@example.com",
        is_enabled=True,
    )

    request_data = request.model_dump(mode="json")
    del request_data["full_name"]

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert "full_name" in str(body)
    assert "Field required" in str(body)


@pytest.mark.anyio
async def test_create_professional_with_invalid_email_returns_unprocessable_entity(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de profissional com email inválido.
    O resultado esperado é um erro 422 Unprocessable Entity.
    """
    admin_token: str = await login_user_admin(client)
    request_data = {
        "full_name": "Dr. Carlos Mendes",
        "bio": "Psiquiatra",
        "phone": "+5551955555555",
        "email": "invalid-email",
        "is_enabled": True,
        "specialities": [],
    }

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_professional_with_nonexistent_speciality_returns_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de profissional com especialidade inexistente.
    O resultado esperado é um erro 404 Not Found.
    """
    admin_token: str = await login_user_admin(client)
    fake_speciality_id = uuid.uuid4()
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Laura Fernandes",
        bio="Pediatra",
        phone="+5551944444444",
        email="laura.fernandes@example.com",
        is_enabled=True,
        specialities=[fake_speciality_id],
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json()["detail"]
        == "One or more specialities specified does not exist."
    )


# ==================== UPDATE PROFESSIONAL TESTS ====================


@pytest.mark.anyio
async def test_update_professional_as_admin_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de um profissional por um administrador.
    O resultado esperado é um status 200 OK.
    """
    admin_token: str = await login_user_admin(client)

    # Criar profissional
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Roberto Lima",
        bio="Clínico Geral",
        phone="+5551933333333",
        email="roberto.lima@example.com",
        is_enabled=True,
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Atualizar profissional
    update_request = ProfessionalFactory.create_custom_update_request(
        full_name="Dr. Roberto Lima Atualizado",
        bio="Clínico Geral com 20 anos de experiência",
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["full_name"] == "Dr. Roberto Lima Atualizado"
    assert body["bio"] == "Clínico Geral com 20 anos de experiência"


@pytest.mark.anyio
async def test_update_professional_as_patient_returns_forbidden(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de atualização de profissional por um usuário não-administrador.
    O resultado esperado é um erro 403 Forbidden.
    """
    admin_token: str = await login_user_admin(client)
    patient_token: str = await register_and_login_default_user(client)

    # Criar profissional como admin
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Fernanda Souza",
        bio="Endocrinologista",
        phone="+5551922222222",
        email="fernanda.souza@example.com",
        is_enabled=True,
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Tentar atualizar como paciente
    update_request = ProfessionalFactory.create_custom_update_request(
        full_name="Nome Alterado",
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User does not have admin privileges"


@pytest.mark.anyio
async def test_update_professional_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de atualização de profissional sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    fake_id = uuid.uuid4()
    update_request = ProfessionalFactory.create_custom_update_request(
        full_name="Nome Alterado",
    )

    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{fake_id}",
        json=update_request.model_dump(mode="json"),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_nonexistent_professional_returns_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de um profissional inexistente.
    O resultado esperado é um erro 404 Not Found.
    """
    admin_token: str = await login_user_admin(client)
    fake_id = uuid.uuid4()
    update_request = ProfessionalFactory.create_custom_update_request(
        full_name="Nome Alterado",
    )

    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{fake_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Professional not found."


@pytest.mark.anyio
async def test_update_professional_with_invalid_speciality_returns_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de profissional com especialidade inexistente.
    O resultado esperado é um erro 404 Not Found.
    """
    admin_token: str = await login_user_admin(client)

    # Criar profissional
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Marcos Alves",
        bio="Oftalmologista",
        phone="+5551911111111",
        email="marcos.alves@example.com",
        is_enabled=True,
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Tentar atualizar com especialidade inválida
    fake_speciality_id = uuid.uuid4()
    update_request = ProfessionalFactory.create_custom_update_request(
        specialities=[fake_speciality_id],
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json()["detail"]
        == "One or more specialities specified does not exist."
    )


# ==================== GET ALL PROFESSIONALS (ADMIN) TESTS ====================


@pytest.mark.anyio
async def test_get_all_professionals_as_admin_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem de profissionais por um administrador.
    O resultado esperado é um status 200 OK.
    """
    admin_token: str = await login_user_admin(client)

    # Criar alguns profissionais
    for i in range(3):
        create_request = ProfessionalFactory.create_custom_request(
            full_name=f"Dr. Profissional {i}",
            bio=f"Bio {i}",
            phone=f"+555199999{i:04d}",
            email=f"profissional{i}@example.com",
            is_enabled=True,
        )
        await client.post(
            ADMIN_PROFESSIONAL_URL,
            json=create_request.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    response: Response = await client.get(
        ADMIN_PROFESSIONAL_URL,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 3


@pytest.mark.anyio
async def test_get_all_professionals_as_patient_returns_forbidden(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de listagem de profissionais (endpoint admin) por um não-administrador.
    O resultado esperado é um erro 403 Forbidden.
    """
    patient_token: str = await register_and_login_default_user(client)

    response: Response = await client.get(
        ADMIN_PROFESSIONAL_URL,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User does not have admin privileges"


@pytest.mark.anyio
async def test_get_all_professionals_admin_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de listagem de profissionais sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    response: Response = await client.get(ADMIN_PROFESSIONAL_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_all_professionals_admin_with_limit_and_offset(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem de profissionais com paginação (limit e offset).
    """
    admin_token: str = await login_user_admin(client)

    # Criar alguns profissionais
    for i in range(5):
        create_request = ProfessionalFactory.create_custom_request(
            full_name=f"Dr. Pagination {i}",
            bio=f"Bio pagination {i}",
            phone=f"+555198888{i:04d}",
            email=f"pagination{i}@example.com",
            is_enabled=True,
        )
        await client.post(
            ADMIN_PROFESSIONAL_URL,
            json=create_request.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    response: Response = await client.get(
        f"{ADMIN_PROFESSIONAL_URL}?limit=2&offset=1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert len(body) <= 2


# ==================== GET ALL PROFESSIONALS (PUBLIC) TESTS ====================


@pytest.mark.anyio
async def test_get_all_professionals_public_as_authenticated_user_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem de profissionais habilitados por usuário autenticado não-admin.
    O resultado esperado é um status 200 OK.
    """
    admin_token: str = await login_user_admin(client)
    patient_token: str = await register_and_login_default_user(client)

    # Criar profissionais habilitados e desabilitados
    for i in range(2):
        create_request = ProfessionalFactory.create_custom_request(
            full_name=f"Dr. Enabled {i}",
            bio=f"Bio enabled {i}",
            phone=f"+555197777{i:04d}",
            email=f"enabled{i}@example.com",
            is_enabled=True,
        )
        await client.post(
            ADMIN_PROFESSIONAL_URL,
            json=create_request.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    # Criar profissional desabilitado
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Disabled",
        bio="Bio disabled",
        phone="+5551966660000",
        email="disabled@example.com",
        is_enabled=False,
    )
    await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response: Response = await client.get(
        PUBLIC_PROFESSIONAL_URL,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    # Deve retornar apenas os habilitados
    for professional in body:
        assert "id" in professional
        assert "full_name" in professional


@pytest.mark.anyio
async def test_get_all_professionals_public_unauthenticated_returns_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a tentativa de listagem de profissionais públicos sem autenticação.
    O resultado esperado é um erro 401 Unauthorized.
    """
    response: Response = await client.get(PUBLIC_PROFESSIONAL_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_all_professionals_public_with_limit_and_offset(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem de profissionais públicos com paginação.
    """
    admin_token: str = await login_user_admin(client)
    patient_token: str = await register_and_login_default_user(client)

    # Criar alguns profissionais
    for i in range(5):
        create_request = ProfessionalFactory.create_custom_request(
            full_name=f"Dr. Public Pagination {i}",
            bio=f"Bio public pagination {i}",
            phone=f"+555196666{i:04d}",
            email=f"public_pagination{i}@example.com",
            is_enabled=True,
        )
        await client.post(
            ADMIN_PROFESSIONAL_URL,
            json=create_request.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    response: Response = await client.get(
        f"{PUBLIC_PROFESSIONAL_URL}?limit=2&offset=1",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)
    assert len(body) <= 2


# ==================== PROFESSIONAL WITH SPECIALITIES TESTS ====================

from ga_api.db.models.speciality_model import Speciality


@pytest.mark.anyio
async def test_create_professional_with_valid_speciality_returns_created(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de profissional com especialidade válida existente no banco.
    O resultado esperado é um status 201 Created com a especialidade relacionada.
    """
    admin_token: str = await login_user_admin(client)

    # Inserir especialidade diretamente no banco
    speciality = Speciality(title="Cardiologia")
    dbsession.add(speciality)
    await dbsession.commit()
    await dbsession.refresh(speciality)
    speciality_id = speciality.id

    # Criar profissional com a especialidade
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Cardiologista Silva",
        bio="Especialista em cardiologia",
        phone="+5551920000001",
        email="cardio.silva@example.com",
        is_enabled=True,
        specialities=[speciality_id],
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["full_name"] == "Dr. Cardiologista Silva"
    assert "specialities" in body
    assert len(body["specialities"]) == 1
    assert body["specialities"][0]["id"] == str(speciality_id)
    assert body["specialities"][0]["title"] == "Cardiologia"


@pytest.mark.anyio
async def test_create_professional_with_multiple_specialities_returns_created(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a criação de profissional com múltiplas especialidades válidas.
    O resultado esperado é um status 201 Created com todas as especialidades relacionadas.
    """
    admin_token: str = await login_user_admin(client)

    # Inserir múltiplas especialidades diretamente no banco
    specialities = ["Ortopedia", "Traumatologia", "Medicina Esportiva"]
    speciality_ids = []

    for speciality_title in specialities:
        speciality = Speciality(title=speciality_title)
        dbsession.add(speciality)
        await dbsession.flush()
        speciality_ids.append(speciality.id)

    await dbsession.commit()

    # Criar profissional com múltiplas especialidades
    request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Multi Especialista",
        bio="Profissional com múltiplas especialidades",
        phone="+5551920000002",
        email="multi.especialista@example.com",
        is_enabled=True,
        specialities=speciality_ids,
    )

    response: Response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["full_name"] == "Dr. Multi Especialista"
    assert "specialities" in body
    assert len(body["specialities"]) == 3

    # Verificar que todas as especialidades estão presentes
    returned_titles = {spec["title"] for spec in body["specialities"]}
    assert returned_titles == set(specialities)


@pytest.mark.anyio
async def test_update_professional_with_valid_speciality_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de profissional adicionando especialidade válida.
    O resultado esperado é um status 200 OK com a especialidade relacionada.
    """
    admin_token: str = await login_user_admin(client)

    # Criar profissional sem especialidades
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Sem Especialidade",
        bio="Clínico Geral",
        phone="+5551920000003",
        email="sem.especialidade@example.com",
        is_enabled=True,
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Inserir especialidade diretamente no banco
    speciality = Speciality(title="Pediatria")
    dbsession.add(speciality)
    await dbsession.commit()
    await dbsession.refresh(speciality)
    speciality_id = speciality.id

    # Atualizar profissional adicionando especialidade
    update_request = ProfessionalFactory.create_custom_update_request(
        specialities=[speciality_id],
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "specialities" in body
    assert len(body["specialities"]) == 1
    assert body["specialities"][0]["id"] == str(speciality_id)
    assert body["specialities"][0]["title"] == "Pediatria"


@pytest.mark.anyio
async def test_update_professional_replacing_specialities_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de profissional substituindo suas especialidades.
    O resultado esperado é um status 200 OK com as novas especialidades.
    """
    admin_token: str = await login_user_admin(client)

    # Inserir especialidade inicial
    old_speciality = Speciality(title="Neurologia")
    dbsession.add(old_speciality)
    await dbsession.commit()
    await dbsession.refresh(old_speciality)
    old_speciality_id = old_speciality.id

    # Criar profissional com especialidade inicial
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Especialidade Original",
        bio="Neurologista",
        phone="+5551920000004",
        email="original.especialidade@example.com",
        is_enabled=True,
        specialities=[old_speciality_id],
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Inserir novas especialidades
    new_specialities = ["Psiquiatria", "Psicologia Clínica"]
    new_speciality_ids = []

    for title in new_specialities:
        speciality = Speciality(title=title)
        dbsession.add(speciality)
        await dbsession.flush()
        new_speciality_ids.append(speciality.id)

    await dbsession.commit()

    # Atualizar profissional substituindo especialidades
    update_request = ProfessionalFactory.create_custom_update_request(
        specialities=new_speciality_ids,
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "specialities" in body
    assert len(body["specialities"]) == 2

    # Verificar que as novas especialidades estão presentes
    returned_titles = {spec["title"] for spec in body["specialities"]}
    assert returned_titles == set(new_specialities)

    # Verificar que a especialidade antiga não está mais presente
    returned_ids = {spec["id"] for spec in body["specialities"]}
    assert str(old_speciality_id) not in returned_ids


@pytest.mark.anyio
async def test_update_professional_removing_all_specialities_returns_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização de profissional removendo todas as especialidades.
    O resultado esperado é um status 200 OK sem especialidades.
    """
    admin_token: str = await login_user_admin(client)

    # Inserir especialidade
    speciality_dao = SpecialityDAO(dbsession)
    speciality = Speciality(title="Dermatologia")
    await save_and_expect(speciality_dao, speciality, 1)

    saved_specialities_list = await speciality_dao.find_all()
    saved_speciality = saved_specialities_list[0]

    speciality_id = saved_speciality.id

    # Criar profissional com especialidade
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Com Especialidade",
        bio="Dermatologista",
        phone="+5551920000005",
        email="com.especialidade@example.com",
        is_enabled=True,
        specialities=[speciality_id],
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Atualizar profissional removendo todas as especialidades
    update_request = ProfessionalFactory.create_custom_update_request(
        specialities=[],
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "specialities" in body
    assert len(body["specialities"]) == 0


@pytest.mark.anyio
async def test_update_professional_with_mixed_valid_invalid_specialities_returns_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a atualização com lista contendo especialidades válidas e inválidas.
    O resultado esperado é um erro 404 Not Found.
    """
    admin_token: str = await login_user_admin(client)

    # Criar profissional
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Test Mixed",
        bio="Test",
        phone="+5551920000006",
        email="test.mixed@example.com",
        is_enabled=True,
    )
    create_response = await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    professional_id = create_response.json()["id"]

    # Inserir especialidade válida
    speciality = Speciality(title="Endocrinologia")
    dbsession.add(speciality)
    await dbsession.commit()
    await dbsession.refresh(speciality)
    valid_speciality_id = speciality.id

    # Tentar atualizar com uma especialidade válida e uma inválida
    fake_speciality_id = uuid.uuid4()
    update_request = ProfessionalFactory.create_custom_update_request(
        specialities=[valid_speciality_id, fake_speciality_id],
    )
    response: Response = await client.put(
        f"{ADMIN_PROFESSIONAL_URL}{professional_id}",
        json=update_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json()["detail"]
        == "One or more specialities specified does not exist."
    )


@pytest.mark.anyio
async def test_get_all_professionals_returns_specialities_correctly(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem de profissionais e verifica se as especialidades
    são retornadas corretamente no response.
    """
    admin_token: str = await login_user_admin(client)

    # Inserir especialidades
    speciality1 = Speciality(title="Ginecologia")
    speciality2 = Speciality(title="Obstetrícia")
    dbsession.add_all([speciality1, speciality2])
    await dbsession.commit()
    await dbsession.refresh(speciality1)
    await dbsession.refresh(speciality2)

    # Criar profissional com especialidades
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dra. Ginecologista",
        bio="Especialista em saúde da mulher",
        phone="+5551920000007",
        email="ginecologista@example.com",
        is_enabled=True,
        specialities=[speciality1.id, speciality2.id],
    )
    await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Criar profissional sem especialidades
    create_request2 = ProfessionalFactory.create_custom_request(
        full_name="Dr. Sem Especialidades",
        bio="Clínico geral",
        phone="+5551920000008",
        email="sem.espec@example.com",
        is_enabled=True,
    )
    await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request2.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Listar todos os profissionais
    response: Response = await client.get(
        ADMIN_PROFESSIONAL_URL,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)

    # Encontrar o profissional com especialidades
    professional_with_specs = next(
        (p for p in body if p["full_name"] == "Dra. Ginecologista"), None
    )
    assert professional_with_specs is not None
    assert "specialities" in professional_with_specs
    assert len(professional_with_specs["specialities"]) == 2

    spec_titles = {spec["title"] for spec in professional_with_specs["specialities"]}
    assert spec_titles == {"Ginecologia", "Obstetrícia"}

    # Verificar que cada especialidade tem id e title
    for spec in professional_with_specs["specialities"]:
        assert "id" in spec
        assert "title" in spec
        assert isinstance(spec["id"], str)
        assert isinstance(spec["title"], str)

    # Encontrar o profissional sem especialidades
    professional_without_specs = next(
        (p for p in body if p["full_name"] == "Dr. Sem Especialidades"), None
    )
    assert professional_without_specs is not None
    assert "specialities" in professional_without_specs
    assert len(professional_without_specs["specialities"]) == 0


@pytest.mark.anyio
async def test_get_public_professionals_returns_specialities_correctly(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """
    Testa a listagem pública de profissionais e verifica se as especialidades
    são retornadas corretamente.
    """
    admin_token: str = await login_user_admin(client)
    patient_token: str = await register_and_login_default_user(client)

    # Inserir especialidades
    speciality1 = Speciality(title="Urologia")
    speciality2 = Speciality(title="Nefrologia")
    dbsession.add_all([speciality1, speciality2])
    await dbsession.commit()
    await dbsession.refresh(speciality1)
    await dbsession.refresh(speciality2)

    # Criar profissional habilitado com especialidades
    create_request = ProfessionalFactory.create_custom_request(
        full_name="Dr. Urologista Público",
        bio="Especialista em urologia",
        phone="+5551920000009",
        email="uro.publico@example.com",
        is_enabled=True,
        specialities=[speciality1.id, speciality2.id],
    )
    await client.post(
        ADMIN_PROFESSIONAL_URL,
        json=create_request.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Listar profissionais como usuário não-admin
    response: Response = await client.get(
        PUBLIC_PROFESSIONAL_URL,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert isinstance(body, list)

    # Encontrar o profissional criado
    professional = next(
        (p for p in body if p["full_name"] == "Dr. Urologista Público"), None
    )
    assert professional is not None
    assert "specialities" in professional
    assert len(professional["specialities"]) == 2

    spec_titles = {spec["title"] for spec in professional["specialities"]}
    assert spec_titles == {"Urologia", "Nefrologia"}

    # Verificar estrutura das especialidades
    for spec in professional["specialities"]:
        assert "id" in spec
        assert "title" in spec
