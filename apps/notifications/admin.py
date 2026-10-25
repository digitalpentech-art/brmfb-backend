from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'customer', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'customer__customer_number')
    list_filter = ('channel', 'is_read')
