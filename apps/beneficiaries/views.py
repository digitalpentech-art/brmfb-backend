from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Beneficiary
from .serializers import BeneficiarySerializer


class BeneficiaryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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

        beneficiaries = Beneficiary.objects.filter(customer=customer)
        serializer = BeneficiarySerializer(beneficiaries, many=True)
        return Response({
            "success": True,
            "code": "BENEFICIARIES_RETRIEVED",
            "message": "Beneficiaries retrieved successfully.",
            "data": serializer.data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)

    def post(self, request):
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

        serializer = BeneficiarySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid beneficiary data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        beneficiary = serializer.save(customer=customer)
        return Response({
            "success": True,
            "code": "BENEFICIARY_CREATED",
            "message": "Beneficiary saved successfully.",
            "data": BeneficiarySerializer(beneficiary).data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_201_CREATED)


class BeneficiaryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, beneficiary_id):
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

        try:
            beneficiary = Beneficiary.objects.get(id=beneficiary_id, customer=customer)
        except Beneficiary.DoesNotExist:
            return Response({
                "success": False,
                "code": "BENEFICIARY_NOT_FOUND",
                "message": "Beneficiary not found.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_404_NOT_FOUND)

        beneficiary.delete()
        return Response({
            "success": True,
            "code": "BENEFICIARY_DELETED",
            "message": "Beneficiary deleted successfully.",
            "data": None,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)
