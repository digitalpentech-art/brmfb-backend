from django.contrib import admin
from .models import Beneficiary

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'account_number', 'bank_name', 'customer', 'is_favorite')
    search_fields = ('account_name', 'account_number', 'customer__customer_number')
    list_filter = ('is_favorite', 'bank_name')
