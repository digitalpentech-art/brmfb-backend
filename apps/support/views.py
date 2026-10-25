from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import SupportTicket
from .serializers import SupportTicketSerializer, SupportTicketStatusUpdateSerializer
from .services import SupportService
from apps.common.permissions import IsSupport


class SupportTicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            tickets = SupportTicket.objects.all()
        else:
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
            tickets = SupportTicket.objects.filter(customer=customer)

        serializer = SupportTicketSerializer(tickets, many=True)
        return Response({
            "success": True,
            "code": "TICKETS_RETRIEVED",
            "message": "Support tickets retrieved successfully.",
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

        serializer = SupportTicketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid ticket data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        ip_address = request.META.get('REMOTE_ADDR')
        ticket = SupportService.create_ticket(
            customer=customer,
            category=data.get('category', 'GENERAL'),
            subject=data['subject'],
            description=data['description'],
            user=request.user,
            ip_address=ip_address
        )

        return Response({
            "success": True,
            "code": "TICKET_CREATED",
            "message": "Support ticket created successfully.",
            "data": SupportTicketSerializer(ticket).data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_201_CREATED)


class SupportTicketStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsSupport]

    def patch(self, request, ticket_id):
        serializer = SupportTicketStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid status.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket = SupportService.update_ticket_status(
                ticket_id=ticket_id,
                new_status=serializer.validated_data['status'],
                staff_user=request.user
            )
            return Response({
                "success": True,
                "code": "TICKET_UPDATED",
                "message": "Support ticket status updated successfully.",
                "data": SupportTicketSerializer(ticket).data,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "success": False,
                "code": "UPDATE_FAILED",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)
