from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Account
from .services import AccountService
from .serializers import AccountSerializer


class AccountListView(APIView):
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

        service = AccountService()
        accounts = service.get_customer_accounts(customer)
        serializer = AccountSerializer(accounts, many=True)

        return Response({
            "success": True,
            "code": "ACCOUNTS_RETRIEVED",
            "message": "Accounts retrieved successfully.",
            "data": serializer.data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):
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

        service = AccountService()
        try:
            account_data = service.get_account_details_with_balance(account_id, customer)
            return Response({
                "success": True,
                "code": "ACCOUNT_BALANCE_RETRIEVED",
                "message": "Authoritative account balance retrieved successfully.",
                "data": account_data,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({
                "success": False,
                "code": "ACCOUNT_NOT_FOUND",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_404_NOT_FOUND)
