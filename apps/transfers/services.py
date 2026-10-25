from django.db import transaction
from django.core.exceptions import ValidationError
from apps.accounts.models import Account
from apps.transactions.services import TransactionService
from integrations.core_banking.mock import MockCoreBankingProvider


class TransferService:
    def __init__(self, provider=None):
        self.provider = provider or MockCoreBankingProvider()

    @transaction.atomic
    def execute_transfer(
        self,
        customer,
        source_account_id,
        amount,
        beneficiary_account_number,
        beneficiary_bank_code,
        beneficiary_account_name,
        idempotency_key,
        narration="",
        user=None,
        ip_address=None
    ):
        if amount <= 0:
            raise ValidationError("Transfer amount must be greater than zero.")

        try:
            source_account = Account.objects.get(id=source_account_id, customer=customer)
        except Account.DoesNotExist:
            raise ValidationError("Source account not found or access denied.")

        if source_account.status != 'ACTIVE':
            raise ValidationError("Source account is not active.")

        # 1. Create transaction via TransactionService (enforces idempotency)
        tx, is_duplicate = TransactionService.create_transaction(
            idempotency_key=idempotency_key,
            transaction_type='TRANSFER',
            amount=amount,
            source_account=source_account,
            metadata={
                "beneficiary_account_number": beneficiary_account_number,
                "beneficiary_bank_code": beneficiary_bank_code,
                "beneficiary_account_name": beneficiary_account_name,
                "narration": narration
            },
            user=user,
            ip_address=ip_address
        )

        if is_duplicate:
            return tx, True

        # 2. Update status to PROCESSING
        tx = TransactionService.update_transaction_status(tx.id, 'PROCESSING', user=user)

        # 3. Call Core Banking Provider for transfer
        provider_payload = {
            "source_account": source_account.external_account_reference,
            "destination_account": beneficiary_account_number,
            "bank_code": beneficiary_bank_code,
            "amount": float(amount),
            "narration": narration
        }

        try:
            provider_response = self.provider.initiate_transfer(provider_payload)
            ext_ref = provider_response.get("external_reference")
            provider_status = provider_response.get("status")

            if provider_status == 'SUCCESSFUL':
                tx = TransactionService.update_transaction_status(
                    tx.id, 'SUCCESSFUL', external_reference=ext_ref, user=user
                )
            else:
                tx = TransactionService.update_transaction_status(
                    tx.id, 'FAILED', failure_reason=provider_response.get("message", "Provider failed transfer."), user=user
                )
        except Exception as e:
            tx = TransactionService.update_transaction_status(
                tx.id, 'FAILED', failure_reason=str(e), user=user
            )

        return tx, False
