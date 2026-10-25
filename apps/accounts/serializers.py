from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number_masked', 'account_type', 'currency', 'status', 'created_at']
        read_only_fields = ['id', 'account_number_masked', 'account_type', 'currency', 'status', 'created_at']
