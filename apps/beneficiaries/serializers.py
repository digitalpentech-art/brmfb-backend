from rest_framework import serializers
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = ['id', 'account_number', 'account_name', 'bank_code', 'bank_name', 'is_favorite', 'created_at']
        read_only_fields = ['id', 'created_at']
