from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('category', 'customer_reference', 'biller_code', 'transaction', 'created_at')
    search_fields = ('customer_reference', 'biller_code', 'transaction__reference')
    list_filter = ('category',)
