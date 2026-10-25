from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import PaymentRequestSerializer
from .services import PaymentService
from apps.transactions.serializers import TransactionSerializer


class BasePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    category = 'AIRTIME'

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key") or request.data.get("idempotency_key")
        if not idempotency_key:
            return Response({
                "success": False,
                "code": "IDEMPOTENCY_KEY_REQUIRED",
                "message": "Idempotency-Key header is required for payments.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid payment data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = request.user.customer_profile
        except AttributeError:
            return Response({
                "success": False,
                "code": "PROFILE_NOT_FOUND",
                "message": "Customer profile not found.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_403_FORBIDDEN)

        data = serializer.validated_data
        try:
            ip_address = request.META.get('REMOTE_ADDR')
            tx, payment, is_duplicate = PaymentService.process_payment(
                customer=customer,
                source_account_id=data['source_account_id'],
                category=self.category,
                amount=data['amount'],
                customer_reference=data['customer_reference'],
                idempotency_key=idempotency_key,
                biller_code=data.get('biller_code'),
                biller_item_code=data.get('biller_item_code'),
                user=request.user,
                ip_address=ip_address
            )

            tx_data = TransactionSerializer(tx).data
            tx_data['token_or_receipt'] = payment.token_or_receipt if payment else None
            status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED

            return Response({
                "success": True,
                "code": f"{self.category}_PAYMENT_PROCESSED",
                "message": "Payment processed successfully." if not is_duplicate else "Idempotent duplicate payment returned.",
                "data": tx_data,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status_code)
        except ValidationError as e:
            return Response({
                "success": False,
                "code": "PAYMENT_FAILED",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)


class AirtimePaymentView(BasePaymentView):
    category = 'AIRTIME'


class DataPaymentView(BasePaymentView):
    category = 'DATA'


class BillPaymentView(BasePaymentView):
    category = 'BILL'


class QRPaymentView(BasePaymentView):
    category = 'QR'
