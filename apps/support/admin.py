from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'category', 'status', 'customer', 'assigned_staff', 'created_at')
    search_fields = ('subject', 'description', 'customer__customer_number')
    list_filter = ('category', 'status')
