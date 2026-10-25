from rest_framework import serializers


class PaymentRequestSerializer(serializers.Serializer):
    source_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    customer_reference = serializers.CharField(max_length=150)
    biller_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    biller_item_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
