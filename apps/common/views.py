from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness probe to check if the application is running.
    """
    return Response({
        "status": "alive",
        "service": "brmfb-backend",
        "version": "1.0.0"
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness probe to check if database and critical dependencies are accessible.
    """
    db_status = "healthy"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = "unhealthy"

    status_code = status.HTTP_200_OK if db_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response({
        "status": "ready" if db_status == "healthy" else "not_ready",
        "database": db_status,
        "service": "brmfb-backend"
    }, status=status_code)
