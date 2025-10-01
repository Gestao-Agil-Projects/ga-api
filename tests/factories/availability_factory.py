import uuid
from datetime import datetime, timedelta, timezone
from ga_api.web.api.availability.request.availability_request import AvailabilityRequest


class AvailabilityFactory:
    @staticmethod
    def create_default_request() -> AvailabilityRequest:
        """
        Cria um request de disponibilidade padrão para os testes.
        Ex: amanhã, das 10:00 às 11:00 UTC.
        """
        start_time = datetime.now(timezone.utc).replace(
            hour=10, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        return AvailabilityRequest(
            professional_id=uuid.uuid4(),
            start_time=start_time,
            end_time=end_time,
        )

    @staticmethod
    def create_custom_request(
        start_time: datetime,
        end_time: datetime,
        professional_id: uuid.UUID = uuid.uuid4(),
    ) -> AvailabilityRequest:
        """
        Cria um request de disponibilidade com horários customizados.
        """
        return AvailabilityRequest(
            professional_id=professional_id,
            start_time=start_time,
            end_time=end_time,
        )
