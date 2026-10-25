from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'amount', 'currency', 'transaction_type',
            'status', 'failure_reason', 'external_provider_reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
