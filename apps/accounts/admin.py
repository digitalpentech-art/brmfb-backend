from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number_masked', 'customer', 'account_type', 'currency', 'status', 'created_at')
    search_fields = ('account_number_masked', 'external_account_reference', 'customer__customer_number')
    list_filter = ('account_type', 'currency', 'status')
