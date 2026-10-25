import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class CustomerProfile(models.Model):
    KYC_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('REVIEW_REQUIRED', 'Review Required'),
        ('SUSPENDED', 'Suspended'),
    ]

    ACCOUNT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FROZEN', 'Frozen'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    customer_number = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(db_index=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    kyc_status = models.CharField(max_length=30, choices=KYC_STATUS_CHOICES, default='PENDING')
    account_status = models.CharField(max_length=30, choices=ACCOUNT_STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_profile'
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'

    def __str__(self):
        return f"{self.customer_number} - {self.first_name} {self.last_name}"
