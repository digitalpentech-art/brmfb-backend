from .models import AuditEvent, SecurityEvent


class AuditService:
    @staticmethod
    def log_event(user, event_type, description, ip_address=None, metadata=None):
        try:
            AuditEvent.objects.create(
                user=user if user and user.is_authenticated else None,
                event_type=event_type,
                description=description,
                ip_address=ip_address,
                metadata=metadata or {}
            )
        except Exception:
            pass

    @staticmethod
    def log_security_event(user, event_type, description, ip_address=None, metadata=None):
        try:
            SecurityEvent.objects.create(
                user=user if user and user.is_authenticated else None,
                event_type=event_type,
                description=description,
                ip_address=ip_address,
                metadata=metadata or {}
            )
        except Exception:
            pass
