import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.support.models import SupportTicket


@pytest.mark.django_db
class TestSupportSystem:
    def test_customer_create_support_ticket(self):
        user = User.objects.create_user(
            email="ticketuser@brmfb.ng",
            phone_number="08055667788",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB77770000",
            first_name="Lawan",
            last_name="Gana",
            phone="08055667788",
            email="ticketuser@brmfb.ng"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('support-ticket-list-create')
        payload = {
            "category": "TRANSACTION",
            "subject": "Delayed Transfer Confirmation",
            "description": "My transfer from savings to another bank has not reflected."
        }
        res = client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['success'] is True
        assert res.data['data']['subject'] == "Delayed Transfer Confirmation"
        assert res.data['data']['status'] == "OPEN"

    def test_staff_update_ticket_status(self):
        staff_user = User.objects.create_user(
            email="staff@brmfb.ng",
            phone_number="08000009999",
            password="StaffPassword123!",
            is_staff=True
        )
        customer_user = User.objects.create_user(
            email="cust@brmfb.ng",
            phone_number="08011110000",
            password="CustomerPassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=customer_user,
            customer_number="BRMFB44441111",
            first_name="Aisha",
            last_name="Bukar",
            phone="08011110000",
            email="cust@brmfb.ng"
        )
        ticket = SupportTicket.objects.create(
            customer=profile,
            category="GENERAL",
            subject="App Login Issue",
            description="Unable to login on Android app.",
            status="OPEN"
        )

        client = APIClient()
        client.force_authenticate(user=staff_user)

        url = reverse('support-ticket-status-update', kwargs={'ticket_id': ticket.id})
        payload = {"status": "RESOLVED"}
        res = client.patch(url, payload, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['success'] is True
        assert res.data['data']['status'] == "RESOLVED"
