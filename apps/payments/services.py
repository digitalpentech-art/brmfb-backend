import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.accounts.models import Account
from apps.transactions.services import TransactionService
from .models import Payment


class PaymentService:
    @staticmethod
    @transaction.atomic
    def process_payment(
        customer,
        source_account_id,
        category,
        amount,
        customer_reference,
        idempotency_key,
        biller_code=None,
        biller_item_code=None,
        user=None,
        ip_address=None
    ):
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")

        try:
            source_account = Account.objects.get(id=source_account_id, customer=customer)
        except Account.DoesNotExist:
            raise ValidationError("Source account not found or access denied.")

        if source_account.status != 'ACTIVE':
            raise ValidationError("Source account is not active.")

        tx_type_map = {
            'AIRTIME': 'AIRTIME',
            'DATA': 'DATA',
            'BILL': 'BILL',
            'QR': 'BILL'
        }
        tx_type = tx_type_map.get(category, 'BILL')

        # 1. Create transaction via TransactionService (idempotency enforcement)
        tx, is_duplicate = TransactionService.create_transaction(
            idempotency_key=idempotency_key,
            transaction_type=tx_type,
            amount=amount,
            source_account=source_account,
            metadata={
                "category": category,
                "customer_reference": customer_reference,
                "biller_code": biller_code,
                "biller_item_code": biller_item_code
            },
            user=user,
            ip_address=ip_address
        )

        if is_duplicate:
            payment = Payment.objects.filter(transaction=tx).first()
            return tx, payment, True

        # 2. Update status to PROCESSING
        tx = TransactionService.update_transaction_status(tx.id, 'PROCESSING', user=user)

        # 3. Simulate provider payment execution & token/receipt generation
        ext_ref = f"BRMFB-PAY-{uuid.uuid4().hex[:12].upper()}"
        token_or_receipt = f"RCPT-{random_token_gen()}" if category != 'AIRTIME' else None

        tx = TransactionService.update_transaction_status(
            tx.id, 'SUCCESSFUL', external_reference=ext_ref, user=user
        )

        payment = Payment.objects.create(
            transaction=tx,
            category=category,
            biller_code=biller_code,
            biller_item_code=biller_item_code,
            customer_reference=customer_reference,
            token_or_receipt=token_or_receipt
        )

        return tx, payment, False


def random_token_gen():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
