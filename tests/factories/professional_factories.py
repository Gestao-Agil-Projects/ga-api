from uuid import uuid4
from datetime import datetime, timedelta

# Importe os modelos finais que você criou
from ga_api.db.models.professionals_model import Professional
from ga_api.db.models.availability_model import Availability
from ga_api.enums.availability_status import AvailabilityStatus


class ProfessionalFactory:
    @staticmethod
    def create_db_model(**kwargs) -> Professional:
        """
        Cria uma instância do modelo SQLAlchemy de Professional,
        compatível com a definição final.
        """
        defaults = {
            "full_name": "Dr. House",
            "email": f"house.{uuid4()}@example.com",  # Email único para cada teste
            "bio": "Médico de testes.",
            "phone": "51999998888",
            "is_enabled": True,
        }
        defaults.update(kwargs)
        return Professional(**defaults)


class AvailabilityFactory:
    @staticmethod
    def create_db_model(professional_id: uuid4, **kwargs) -> Availability:
        """Cria uma instância do modelo SQLAlchemy de Availability."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        defaults = {
            "professional_id": professional_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": AvailabilityStatus.AVAILABLE,
        }
        defaults.update(kwargs)
        return Availability(**defaults)
