from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Transaction
from .serializers import TransactionSerializer
from apps.accounts.models import Account


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = request.user.customer_profile
        except AttributeError:
            return Response({
                "success": False,
                "code": "PROFILE_NOT_FOUND",
                "message": "Customer profile not found for user.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_403_FORBIDDEN)

        customer_accounts = Account.objects.filter(customer=customer)
        transactions = Transaction.objects.filter(
            Q(source_account__in=customer_accounts) | Q(destination_account__in=customer_accounts)
        ).distinct()

        serializer = TransactionSerializer(transactions, many=True)

        return Response({
            "success": True,
            "code": "TRANSACTIONS_RETRIEVED",
            "message": "Transactions retrieved successfully.",
            "data": serializer.data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)
