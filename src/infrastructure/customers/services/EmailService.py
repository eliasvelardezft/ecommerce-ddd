import logging

logger = logging.getLogger(__name__)


class EmailService:
    async def send_welcome_email(self, email: str, name: str) -> None:
        """Send welcome email using primitive types"""
        logger.info(f"Sending welcome email to {email}: hi {name}!")
        # TODO: Implement actual email sending logic
