from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import AccountVerificationSerializer, TransferSerializer
from .services import TransferService
from integrations.core_banking.mock import MockCoreBankingProvider
from apps.transactions.serializers import TransactionSerializer


class AccountVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        provider = MockCoreBankingProvider()
        verification_result = provider.verify_account_number(data['account_number'])

        return Response({
            "success": True,
            "code": "ACCOUNT_VERIFIED",
            "message": "Account verified successfully.",
            "data": verification_result,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)


class TransferExecuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key") or request.data.get("idempotency_key")
        if not idempotency_key:
            return Response({
                "success": False,
                "code": "IDEMPOTENCY_KEY_REQUIRED",
                "message": "Idempotency-Key header or field is required for financial transfers.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = TransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid transfer data.",
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
        service = TransferService()

        try:
            ip_address = request.META.get('REMOTE_ADDR')
            tx, is_duplicate = service.execute_transfer(
                customer=customer,
                source_account_id=data['source_account_id'],
                amount=data['amount'],
                beneficiary_account_number=data['beneficiary_account_number'],
                beneficiary_bank_code=data['beneficiary_bank_code'],
                beneficiary_account_name=data['beneficiary_account_name'],
                idempotency_key=idempotency_key,
                narration=data.get('narration', ''),
                user=request.user,
                ip_address=ip_address
            )

            tx_serializer = TransactionSerializer(tx)
            status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED

            return Response({
                "success": True,
                "code": "TRANSFER_PROCESSED",
                "message": "Transfer processed successfully." if not is_duplicate else "Idempotent duplicate transfer returned.",
                "data": tx_serializer.data,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status_code)
        except ValidationError as e:
            return Response({
                "success": False,
                "code": "TRANSFER_FAILED",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)
