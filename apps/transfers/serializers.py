from rest_framework import serializers


class AccountVerificationSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=20)


class TransferSerializer(serializers.Serializer):
    source_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    beneficiary_account_number = serializers.CharField(max_length=20)
    beneficiary_bank_code = serializers.CharField(max_length=20)
    beneficiary_account_name = serializers.CharField(max_length=150)
    narration = serializers.CharField(required=False, allow_blank=True, max_length=255)
