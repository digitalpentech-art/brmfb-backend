from integrations.notifications.mock import MockNotificationProvider
from .models import Notification


class NotificationService:
    def __init__(self, provider=None):
        self.provider = provider or MockNotificationProvider()

    def send_notification(self, customer, title, message, channel='PUSH', metadata=None):
        # 1. Dispatch via Provider
        if channel == 'PUSH':
            # Get active device push tokens for customer
            push_tokens = list(customer.user.devices.filter(is_active=True).exclude(push_token__isnull=True).values_list('push_token', flat=True))
            for token in push_tokens:
                self.provider.send_push(token, title, message, metadata)
        elif channel == 'SMS':
            self.provider.send_sms(customer.phone, message)
        elif channel == 'EMAIL':
            self.provider.send_email(customer.email, title, message)

        # 2. Persist notification record
        notification = Notification.objects.create(
            customer=customer,
            title=title,
            message=message,
            channel=channel,
            metadata=metadata or {}
        )
        return notification
