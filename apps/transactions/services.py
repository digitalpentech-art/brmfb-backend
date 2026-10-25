import random
import string
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Transaction, LedgerEntry
from apps.audit.services import AuditService


class TransactionService:
    VALID_TRANSITIONS = {
        'INITIATED': ['PROCESSING', 'FAILED', 'SUCCESSFUL', 'UNKNOWN'],
        'PROCESSING': ['SUCCESSFUL', 'FAILED', 'REVERSED', 'UNKNOWN'],
        'SUCCESSFUL': ['REVERSED'],
        'FAILED': [],
        'REVERSED': [],
        'UNKNOWN': ['SUCCESSFUL', 'FAILED', 'REVERSED'],
    }

    @staticmethod
    @transaction.atomic
    def create_transaction(
        idempotency_key,
        transaction_type,
        amount,
        source_account=None,
        destination_account=None,
        currency="NGN",
        metadata=None,
        user=None,
        ip_address=None
    ):
        # 1. Idempotency Check
        existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing, True  # True indicates idempotent duplicate return

        reference = f"BRMFB-TX-{random.randint(100000000, 999999999)}"
        while Transaction.objects.filter(reference=reference).exists():
            reference = f"BRMFB-TX-{random.randint(100000000, 999999999)}"

        tx = Transaction.objects.create(
            idempotency_key=idempotency_key,
            reference=reference,
            source_account=source_account,
            destination_account=destination_account,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            status='INITIATED',
            metadata=metadata or {}
        )

        # Create Ledger Entries if accounts involved
        if source_account:
            LedgerEntry.objects.create(
                transaction=tx,
                account=source_account,
                entry_type='DEBIT',
                amount=amount
            )

        if destination_account:
            LedgerEntry.objects.create(
                transaction=tx,
                account=destination_account,
                entry_type='CREDIT',
                amount=amount
            )

        AuditService.log_event(
            user=user,
            event_type="TRANSACTION_INITIATED",
            description=f"Transaction {reference} of {amount} {currency} initiated.",
            ip_address=ip_address,
            metadata={"transaction_id": str(tx.id), "reference": reference, "type": transaction_type}
        )

        return tx, False

    @staticmethod
    @transaction.atomic
    def update_transaction_status(transaction_id, new_status, failure_reason=None, external_reference=None, user=None):
        try:
            tx = Transaction.objects.select_for_update().get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise ValidationError("Transaction not found.")

        current_status = tx.status
        allowed_next = TransactionService.VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next and new_status != current_status:
            raise ValidationError(f"Invalid state transition from {current_status} to {new_status}.")

        tx.status = new_status
        if failure_reason:
            tx.failure_reason = failure_reason
        if external_reference:
            tx.external_provider_reference = external_reference
        tx.save()

        AuditService.log_event(
            user=user,
            event_type=f"TRANSACTION_{new_status}",
            description=f"Transaction {tx.reference} updated to {new_status}.",
            metadata={"transaction_id": str(tx.id), "reference": tx.reference, "status": new_status}
        )

        return tx
