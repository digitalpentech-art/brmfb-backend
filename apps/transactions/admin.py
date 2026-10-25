from django.contrib import admin
from .models import Transaction, LedgerEntry

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'transaction_type', 'amount', 'currency', 'status', 'created_at')
    search_fields = ('reference', 'idempotency_key', 'external_provider_reference')
    list_filter = ('transaction_type', 'status', 'currency')

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'account', 'entry_type', 'amount', 'created_at')
    search_fields = ('transaction__reference', 'account__account_number_masked')
    list_filter = ('entry_type',)
