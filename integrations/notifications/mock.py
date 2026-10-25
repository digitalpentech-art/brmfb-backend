import logging
from .base import NotificationProvider

logger = logging.getLogger(__name__)


class MockNotificationProvider(NotificationProvider):
    def send_push(self, push_token: str, title: str, message: str, data: dict = None) -> bool:
        logger.info(f"[MOCK PUSH] To: {push_token[:10]}... | Title: {title} | Message: {message}")
        return True

    def send_sms(self, phone_number: str, message: str) -> bool:
        logger.info(f"[MOCK SMS] To: {phone_number} | Message: {message}")
        return True

    def send_email(self, email: str, subject: str, message: str) -> bool:
        logger.info(f"[MOCK EMAIL] To: {email} | Subject: {subject} | Message: {message}")
        return True
