import uuid
from django.db import models
from django.utils import timezone
from apps.transactions.models import Transaction


class Payment(models.Model):
    PAYMENT_CATEGORY_CHOICES = [
        ('AIRTIME', 'Airtime Purchase'),
        ('DATA', 'Data Bundle'),
        ('BILL', 'Bill Payment'),
        ('QR', 'QR Payment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='payment_details')
    category = models.CharField(max_length=30, choices=PAYMENT_CATEGORY_CHOICES)
    biller_code = models.CharField(max_length=100, blank=True, null=True)
    biller_item_code = models.CharField(max_length=100, blank=True, null=True)
    customer_reference = models.CharField(max_length=150, db_index=True) # phone number, meter number, smartcard number, etc.
    token_or_receipt = models.TextField(blank=True, null=True) # e.g. electricity token or receipt number
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'financial_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.category} - {self.customer_reference} ({self.transaction.reference})"
