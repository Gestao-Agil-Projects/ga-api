# # tests/test_professionals.py
#
# import pytest
# from httpx import AsyncClient
# from fastapi import FastAPI
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette import status
#
# from ga_api.db.dao.professional_dao import ProfessionalDAO
# from ga_api.db.models.professionals_model import Professional
# from ga_api.web.api.professionals.request.professional_create_request import \
#     ProfessionalCreateRequest
# from ga_api.web.api.professionals.request.professional_update_request import \
#     ProfessionalUpdateRequest
# from tests.utils import login_user_admin, save_and_expect
# from ga_api.db.models.specialty_model import Speciality
#
#
# @pytest.fixture
# async def specialty_fixture(dbsession: AsyncSession):
#     """
#     Fixture para criar uma especialidade de teste.
#     """
#     specialty = Speciality(title="Cardiologia")
#     dbsession.add(specialty)
#     await dbsession.commit()
#     await dbsession.refresh(specialty)
#     return specialty
#
#
#
# @pytest.mark.anyio
# async def test_professionals_create (
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     dbsession: AsyncSession,
#     specialty_fixture: Speciality,
# ):
#     """
#     Testa o fluxo completo: criar -> editar -> listar profissionais.
#     """
#     admin_token = await login_user_admin(client)
#     headers = {"Authorization": f"Bearer {admin_token}"}
#
#     # 1. Criar profissional
#     professional_create_request = ProfessionalCreateRequest(
#         full_name="joao",
#         email="joao@email.com",
#         bio="pppp",
#         specialities=[],
#         is_enabled=True,
#         phone="51010010101"
#     )
#
#
#
#     response = await client.post(
#         "/api/admin/professionals",json=professional_create_request.model_dump(mode="json"), headers=headers
#     )
#     assert response.status_code == status.HTTP_201_CREATED
#     created_professional = response.json()
#     professional_id = created_professional["id"]
#
#     assert created_professional["full_name"] == professional_create_request["full_name"]
#     assert created_professional["bio"] == professional_create_request["bio"]
#     assert len(created_professional["specialities"]) == 0
#
#     # 2. Editar profissional
# @pytest.mark.anyio
# async def test_professionals_create(
#         fastapi_app: FastAPI,
#         client: AsyncClient,
#         dbsession: AsyncSession,
#         specialty_fixture: Speciality,
#     ):
#     professional_dao = ProfessionalDAO(dbsession)
#     admin_token = await login_user_admin(client)
#     headers = {"Authorization": f"Bearer {admin_token}"}
#
#
#     professional_model = Professional(
#         full_name="joao",
#         bio="pppp",
#         email="joao@.com",
#     )
#     await save_and_expect(professional_dao, professional_model, 1)
#
#     all_ = await professional_dao.find_all()
#     saved_professional = all_[0]
#     professional_update_request = ProfessionalUpdateRequest(
#         full_name="cleber",
#         bio="clebercleber",
#     )
#
#     response = await client.put(
#         f"/api/admin/professionals/{saved_professional.id}",json=professional_update_request.model_dump(mode="json"), headers=headers
#     )
#     assert response.status_code == status.HTTP_200_OK
#     updated_professional = response.json()
#
#     assert updated_professional["full_name"] == professional_update_request["full_name"]
#     assert updated_professional["bio"] == professional_update_request["bio"]
#
#     # 3. Listar profissionais
#     response = await client.get("/api/admin/professionals", headers=headers)
#     assert response.status_code == status.HTTP_200_OK
#     professionals_list = response.json()
#
#     assert isinstance(professionals_list, list)
#     assert len(professionals_list) > 0
#
#     # Verifica se o profissional criado e atualizado está na lista
#     found = False
#     for prof in professionals_list:
#         if prof["id"] == saved_professional.id:
#             found = True
#             assert prof["full_name"] == professional_update_request["full_name"]
#             assert prof["bio"] == professional_update_request["bio"]
#             assert len(prof["specialities"]) == 0
#             break
#     assert found, "Profissional criado não encontrado na listagem."
