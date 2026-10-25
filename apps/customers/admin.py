from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'first_name', 'last_name', 'phone', 'email', 'kyc_status', 'account_status')
    search_fields = ('customer_number', 'first_name', 'last_name', 'phone', 'email')
    list_filter = ('kyc_status', 'account_status')
