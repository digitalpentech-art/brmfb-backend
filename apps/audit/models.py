import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = 'audit_event'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.event_type}] {self.created_at} - {self.user}"


class SecurityEvent(models.Model):
    EVENT_TYPES = [
        ('MULTIPLE_FAILED_LOGINS', 'Multiple Failed Logins'),
        ('SUSPICIOUS_DEVICE', 'Suspicious Device'),
        ('UNUSUAL_TRANSACTION', 'Unusual Transaction'),
        ('OTP_ABUSE', 'OTP Abuse'),
        ('RATE_LIMIT_TRIGGERED', 'Rate Limit Triggered'),
        ('SESSION_REVOKED', 'Session Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = 'security_event'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.event_type}] {self.created_at} - {self.user}"
