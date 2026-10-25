import uuid
from django.db import models
from django.utils import timezone
from apps.customers.models import CustomerProfile


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', 'Savings Account'),
        ('CURRENT', 'Current Account'),
        ('LOAN', 'Loan Account'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('DORMANT', 'Dormant'),
        ('FROZEN', 'Frozen'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='accounts')
    account_number_masked = models.CharField(max_length=20, db_index=True)
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPE_CHOICES, default='SAVINGS')
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    external_account_reference = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_account'
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        return f"{self.account_number_masked} ({self.account_type})"
