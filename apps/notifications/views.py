from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
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

        notifications = Notification.objects.filter(customer=customer)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            "success": True,
            "code": "NOTIFICATIONS_RETRIEVED",
            "message": "Notifications retrieved successfully.",
            "data": serializer.data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
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
            notification = Notification.objects.get(id=notification_id, customer=customer)
        except Notification.DoesNotExist:
            return Response({
                "success": False,
                "code": "NOTIFICATION_NOT_FOUND",
                "message": "Notification not found.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()

        return Response({
            "success": True,
            "code": "NOTIFICATION_MARKED_READ",
            "message": "Notification marked as read.",
            "data": NotificationSerializer(notification).data,
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)
