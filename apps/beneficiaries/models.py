import uuid
from django.db import models
from django.utils import timezone
from apps.customers.models import CustomerProfile


class Beneficiary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='beneficiaries')
    account_number = models.CharField(max_length=20, db_index=True)
    account_name = models.CharField(max_length=150)
    bank_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=150)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_beneficiary'
        verbose_name = 'Beneficiary'
        verbose_name_plural = 'Beneficiaries'
        unique_together = ('customer', 'account_number', 'bank_code')

    def __str__(self):
        return f"{self.account_name} ({self.account_number} - {self.bank_name})"
