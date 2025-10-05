import uuid
from typing import List, Optional

from ga_api.web.api.professionals.request.professional_create_request import (
    ProfessionalCreateRequest,
)
from ga_api.web.api.professionals.request.professional_update_request import (
    ProfessionalUpdateRequest,
)


class ProfessionalFactory:
    @staticmethod
    def create_default_request() -> ProfessionalCreateRequest:
        return ProfessionalCreateRequest(
            full_name="Dr. Test Professional",
            bio="This is a test professional",
            phone="+5551900000000",
            email="test.professional@example.com",
            is_enabled=True,
            specialities=[],
        )

    @staticmethod
    def create_custom_request(
        full_name: str = "Dr. Custom Professional",
        bio: Optional[str] = None,
        phone: str = "+5551900000001",
        email: str = "custom.professional@example.com",
        is_enabled: bool = True,
        specialities: Optional[List[uuid.UUID]] = None,
    ) -> ProfessionalCreateRequest:
        return ProfessionalCreateRequest(
            full_name=full_name,
            bio=bio,
            phone=phone,
            email=email,
            is_enabled=is_enabled,
            specialities=specialities or [],
        )

    @staticmethod
    def create_default_update_request() -> ProfessionalUpdateRequest:
        return ProfessionalUpdateRequest(
            full_name="Dr. Updated Professional",
            bio="Updated bio",
        )

    @staticmethod
    def create_custom_update_request(
        full_name: Optional[str] = None,
        bio: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        specialities: Optional[List[uuid.UUID]] = None,
    ) -> ProfessionalUpdateRequest:
        return ProfessionalUpdateRequest(
            full_name=full_name,
            bio=bio,
            is_enabled=is_enabled,
            specialities=specialities,
        )
