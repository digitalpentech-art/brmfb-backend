import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile
from apps.accounts.models import Account
from apps.transactions.models import Transaction, LedgerEntry
from apps.transactions.services import TransactionService


@pytest.mark.django_db
class TestTransactionsAndLedger:
    def test_idempotency_transaction_creation(self):
        user = User.objects.create_user(
            email="txuser@brmfb.ng",
            phone_number="08055443322",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB55554444",
            first_name="Ali",
            last_name="Gombe",
            phone="08055443322",
            email="txuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******1122",
            account_type="SAVINGS",
            currency="NGN",
            status="ACTIVE",
            external_account_reference="EXT-TX-001"
        )

        idempotency_key = "unique-key-abc-123"

        # First request
        tx1, is_duplicate1 = TransactionService.create_transaction(
            idempotency_key=idempotency_key,
            transaction_type="DEPOSIT",
            amount=50000.00,
            destination_account=account,
            user=user
        )
        assert not is_duplicate1
        assert tx1.status == 'INITIATED'

        # Second request with same idempotency key
        tx2, is_duplicate2 = TransactionService.create_transaction(
            idempotency_key=idempotency_key,
            transaction_type="DEPOSIT",
            amount=50000.00,
            destination_account=account,
            user=user
        )
        assert is_duplicate2
        assert tx1.id == tx2.id
        assert Transaction.objects.count() == 1

    def test_state_machine_transitions(self):
        user = User.objects.create_user(
            email="smuser@brmfb.ng",
            phone_number="08033221100",
            password="SecurePassword123!"
        )
        account = Account.objects.create(
            customer=CustomerProfile.objects.create(
                user=user, customer_number="BRMFB11110000", first_name="Fati", last_name="Borno",
                phone="08033221100", email="smuser@brmfb.ng"
            ),
            account_number_masked="******9988",
            external_account_reference="EXT-SM-001"
        )

        tx, _ = TransactionService.create_transaction(
            idempotency_key="key-sm-test-1",
            transaction_type="TRANSFER",
            amount=10000.00,
            source_account=account
        )
        assert tx.status == 'INITIATED'

        # Valid transition: INITIATED -> PROCESSING
        tx = TransactionService.update_transaction_status(tx.id, 'PROCESSING')
        assert tx.status == 'PROCESSING'

        # Valid transition: PROCESSING -> SUCCESSFUL
        tx = TransactionService.update_transaction_status(tx.id, 'SUCCESSFUL', external_reference='EXT-PROV-999')
        assert tx.status == 'SUCCESSFUL'
        assert tx.external_provider_reference == 'EXT-PROV-999'

        # Invalid transition: SUCCESSFUL -> PROCESSING (should raise ValidationError)
        with pytest.raises(ValidationError):
            TransactionService.update_transaction_status(tx.id, 'PROCESSING')

    def test_transaction_list_api(self):
        user = User.objects.create_user(
            email="apiuser@brmfb.ng",
            phone_number="08077665544",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB22223333",
            first_name="Bukar",
            last_name="Kano",
            phone="08077665544",
            email="apiuser@brmfb.ng"
        )
        account = Account.objects.create(
            customer=profile,
            account_number_masked="******3344",
            external_account_reference="EXT-API-001"
        )

        TransactionService.create_transaction(
            idempotency_key="api-tx-key-1",
            transaction_type="WITHDRAWAL",
            amount=5000.00,
            source_account=account,
            user=user
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('transaction-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['transaction_type'] == 'WITHDRAWAL'
