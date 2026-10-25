import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.customers.models import CustomerProfile


class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('ACCOUNT', 'Account Inquiry'),
        ('TRANSACTION', 'Transaction Issue'),
        ('TRANSFER', 'Transfer Problem'),
        ('COMPLAINT', 'General Complaint'),
        ('GENERAL', 'General Support'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='support_tickets')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='GENERAL')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_ticket'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.subject} - {self.customer.customer_number}"
