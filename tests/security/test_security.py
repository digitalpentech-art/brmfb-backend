import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.audit.models import SecurityEvent
from apps.audit.services import AuditService


@pytest.mark.django_db
class TestSecurityHardening:
    def test_security_event_logging(self):
        user = User.objects.create_user(
            email="secuser@brmfb.ng",
            phone_number="08000001111",
            password="SecurePassword123!"
        )
        AuditService.log_security_event(
            user=user,
            event_type="MULTIPLE_FAILED_LOGINS",
            description="3 failed login attempts detected.",
            ip_address="192.168.1.50"
        )
        sec_event = SecurityEvent.objects.filter(event_type="MULTIPLE_FAILED_LOGINS").first()
        assert sec_event is not None
        assert sec_event.ip_address == "192.168.1.50"
        assert sec_event.user == user

    def test_unauthenticated_access_blocked(self):
        client = APIClient()
        url = reverse('account-list')
        response = client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
