from pydantic import BaseModel, ConfigDict

from ga_api.web.api.professionals.response.professional_create_response import (
    ProfessionalResponse,
)


class ProfessionalBlockResponse(BaseModel):
    professional: ProfessionalResponse
    is_blocked: bool

    model_config = ConfigDict(from_attributes=True)
