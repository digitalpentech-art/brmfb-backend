from abc import ABC, abstractmethod


class NotificationProvider(ABC):
    @abstractmethod
    def send_push(self, push_token: str, title: str, message: str, data: dict = None) -> bool:
        pass

    @abstractmethod
    def send_sms(self, phone_number: str, message: str) -> bool:
        pass

    @abstractmethod
    def send_email(self, email: str, subject: str, message: str) -> bool:
        pass
