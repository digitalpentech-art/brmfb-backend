import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@pytest.mark.django_db
class TestNotifications:
    def test_send_and_list_notifications(self):
        user = User.objects.create_user(
            email="notifuser@brmfb.ng",
            phone_number="08099112233",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB99990000",
            first_name="Fatima",
            last_name="Ibrahim",
            phone="08099112233",
            email="notifuser@brmfb.ng"
        )

        service = NotificationService()
        notif = service.send_notification(
            customer=profile,
            title="Welcome to BRMFB",
            message="Thank you for banking with Borno Renaissance MFB.",
            channel="SMS"
        )
        assert notif is not None
        assert not notif.is_read

        client = APIClient()
        client.force_authenticate(user=user)

        # List notifications
        list_url = reverse('notification-list')
        res = client.get(list_url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['success'] is True
        assert len(res.data['data']) == 1

        # Mark as read
        read_url = reverse('notification-mark-read', kwargs={'notification_id': notif.id})
        read_res = client.post(read_url)
        assert read_res.status_code == status.HTTP_200_OK
        assert read_res.data['success'] is True
        assert read_res.data['data']['is_read'] is True
