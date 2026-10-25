import uuid
from django.db import models
from django.utils import timezone
from apps.customers.models import CustomerProfile


class Notification(models.Model):
    CHANNEL_CHOICES = [
        ('PUSH', 'Push Notification'),
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='PUSH')
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = 'customer_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] {self.title} - {self.customer.customer_number}"
