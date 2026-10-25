import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.accounts.models import Account


@pytest.mark.django_db
class TestAccountServices:
    def test_list_accounts(self):
        user = User.objects.create_user(
            email="accountuser@brmfb.ng",
            phone_number="08099887766",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB88889999",
            first_name="Zainab",
            last_name="Shettima",
            phone="08099887766",
            email="accountuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******5678",
            account_type="SAVINGS",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-REF-12345"
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('account-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['account_number_masked'] == "******5678"

    def test_get_account_balance_authoritative(self):
        user = User.objects.create_user(
            email="balanceuser@brmfb.ng",
            phone_number="08011223344",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB77776666",
            first_name="Ibrahim",
            last_name="Ali",
            phone="08011223344",
            email="balanceuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******4321",
            account_type="CURRENT",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-REF-98765"
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('account-detail', kwargs={'account_id': account.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['balance'] == 250000.00
        assert response.data['data']['currency'] == "NGN"
        assert response.data['data']['status'] == "ACTIVE"
