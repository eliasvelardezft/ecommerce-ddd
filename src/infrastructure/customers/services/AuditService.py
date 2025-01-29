import logging

from src.domain.customers.Customer import Customer


logger = logging.getLogger(__name__)


class AuditService:
    async def log_event(self, event_name: str, event_data: dict):
        logger.info(f"Logging event: {event_name} with data: {event_data}")
        # TODO: Implement audit logic
