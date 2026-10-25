from django.contrib import admin
from .models import AuditEvent, SecurityEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'ip_address', 'created_at')
    search_fields = ('event_type', 'description', 'user__email', 'ip_address')
    list_filter = ('event_type',)

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'ip_address', 'created_at')
    search_fields = ('event_type', 'description', 'user__email', 'ip_address')
    list_filter = ('event_type',)
