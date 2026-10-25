import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import Account


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PROCESSING', 'Processing'),
        ('SUCCESSFUL', 'Successful'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
        ('UNKNOWN', 'Unknown'),
    ]

    TYPE_CHOICES = [
        ('TRANSFER', 'Bank Transfer'),
        ('AIRTIME', 'Airtime Purchase'),
        ('DATA', 'Data Bundle Purchase'),
        ('BILL', 'Bill Payment'),
        ('DEPOSIT', 'Account Deposit'),
        ('WITHDRAWAL', 'Account Withdrawal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    source_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_transactions')
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    transaction_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='INITIATED')
    failure_reason = models.TextField(blank=True, null=True)
    external_provider_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_transaction'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} ({self.amount} {self.currency}) [{self.status}]"


class LedgerEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='ledger_entries')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='ledger_entries')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = 'financial_ledger_entry'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.entry_type} {self.amount} {self.account.account_number_masked} for {self.transaction.reference}"
