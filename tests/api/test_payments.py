import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.accounts.models import Account
from apps.payments.models import Payment


@pytest.mark.django_db
class TestPayments:
    def test_airtime_purchase(self):
        user = User.objects.create_user(
            email="airtimeuser@brmfb.ng",
            phone_number="08011112222",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB66667777",
            first_name="Zuwaira",
            last_name="Bello",
            phone="08011112222",
            email="airtimeuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******5566",
            account_type="SAVINGS",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-PAY-001"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('payment-airtime')
        payload = {
            "source_account_id": str(account.id),
            "amount": 2000.00,
            "customer_reference": "08011112222",
            "biller_code": "MTN"
        }
        headers = {"HTTP_IDEMPOTENCY_KEY": "airtime-idempotency-key-001"}

        res = client.post(url, payload, **headers, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['success'] is True
        assert res.data['data']['status'] == 'SUCCESSFUL'

        payment = Payment.objects.filter(customer_reference="08011112222").first()
        assert payment is not None
        assert payment.category == 'AIRTIME'

    def test_bill_payment_with_token(self):
        user = User.objects.create_user(
            email="billuser@brmfb.ng",
            phone_number="08033334444",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB88880000",
            first_name="Mustapha",
            last_name="Kano",
            phone="08033334444",
            email="billuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******4433",
            account_type="CURRENT",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-PAY-002"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('payment-bills')
        payload = {
            "source_account_id": str(account.id),
            "amount": 10000.00,
            "customer_reference": "01234567891",
            "biller_code": "PHED",
            "biller_item_code": "PREPAID"
        }
        headers = {"HTTP_IDEMPOTENCY_KEY": "bill-idempotency-key-002"}

        res = client.post(url, payload, **headers, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['success'] is True
        assert res.data['data']['status'] == 'SUCCESSFUL'
        assert 'token_or_receipt' in res.data['data']
        assert res.data['data']['token_or_receipt'] is not None
