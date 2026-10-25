import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.accounts.models import Account
from apps.beneficiaries.models import Beneficiary


@pytest.mark.django_db
class TestTransfersAndBeneficiaries:
    def test_beneficiary_management(self):
        user = User.objects.create_user(
            email="beneficiaryuser@brmfb.ng",
            phone_number="08022334455",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB33334444",
            first_name="Hauwa",
            last_name="Yusuf",
            phone="08022334455",
            email="beneficiaryuser@brmfb.ng"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Create Beneficiary
        create_url = reverse('beneficiary-list-create')
        payload = {
            "account_number": "0123456789",
            "account_name": "Garba Bello",
            "bank_code": "058",
            "bank_name": "Guaranty Trust Bank",
            "is_favorite": True
        }
        res = client.post(create_url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['success'] is True
        assert res.data['data']['account_name'] == "Garba Bello"

        # List Beneficiaries
        list_res = client.get(create_url)
        assert list_res.status_code == status.HTTP_200_OK
        assert len(list_res.data['data']) == 1

    def test_account_verification(self):
        user = User.objects.create_user(
            email="verifyuser@brmfb.ng",
            phone_number="08044556677",
            password="SecurePassword123!"
        )
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('account-verify')
        payload = {
            "account_number": "1002003004",
            "bank_code": "090561"
        }
        res = client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['success'] is True
        assert res.data['data']['account_name'] == "Amina Borno Customer"

    def test_transfer_execution_with_idempotency(self):
        user = User.objects.create_user(
            email="transferuser@brmfb.ng",
            phone_number="08066778899",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB44445555",
            first_name="Abba",
            last_name="Kyari",
            phone="08066778899",
            email="transferuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******7788",
            account_type="SAVINGS",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-TF-001"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        transfer_url = reverse('transfer-execute')
        payload = {
            "source_account_id": str(account.id),
            "amount": 25000.00,
            "beneficiary_account_number": "0123456789",
            "beneficiary_bank_code": "058",
            "beneficiary_account_name": "Garba Bello",
            "narration": "Test transfer"
        }
        headers = {"HTTP_IDEMPOTENCY_KEY": "transfer-key-xyz-789"}

        res = client.post(transfer_url, payload, **headers, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['success'] is True
        assert res.data['data']['status'] == 'SUCCESSFUL'

        # Test duplicate request with same Idempotency-Key
        res_dup = client.post(transfer_url, payload, **headers, format='json')
        assert res_dup.status_code == status.HTTP_200_OK
        assert res_dup.data['success'] is True
        assert res_dup.data['data']['id'] == res.data['data']['id']
