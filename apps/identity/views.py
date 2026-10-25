from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, OTPRequestSerializer, OTPVerifySerializer
from .services import IdentityService, OTPService


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            user, profile = IdentityService.register_customer(
                email=data['email'],
                phone_number=data['phone_number'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data.get('date_of_birth'),
                address=data.get('address')
            )
            # Generate registration OTP
            code, _ = OTPService.generate_otp(user, user.email, 'REGISTRATION')

            return Response({
                "success": True,
                "code": "REGISTRATION_SUCCESS",
                "message": "Customer registered successfully. Please verify your email/phone with the OTP sent.",
                "data": {
                    "customer_number": profile.customer_number,
                    "email": user.email,
                    "mock_otp": code  # Included for dev/demo testing
                },
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "success": False,
                "code": "REGISTRATION_FAILED",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid login data.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = authenticate(email=data['email'], password=data['password'])

        if not user or not user.is_active:
            return Response({
                "success": False,
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_401_UNAUTHORIZED)

        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        session, refresh_token = IdentityService.create_session(
            user=user,
            device_id=data['device_id'],
            platform=data['platform'],
            app_version=data.get('app_version', ''),
            ip_address=ip_address,
            user_agent=user_agent
        )

        return Response({
            "success": True,
            "code": "LOGIN_SUCCESS",
            "message": "Login successful.",
            "data": {
                "email": user.email,
                "is_verified": user.is_verified,
                "session_id": str(session.id),
                "refresh_token": refresh_token
            },
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)


class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid input.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        identifier = data['identifier']
        purpose = data['purpose']

        user = User.objects.filter(email=identifier).first() or User.objects.filter(phone_number=identifier).first()
        code, _ = OTPService.generate_otp(user, identifier, purpose)

        return Response({
            "success": True,
            "code": "OTP_SENT",
            "message": "OTP sent successfully.",
            "data": {
                "mock_otp": code  # For dev/testing mock environment
            },
            "request_id": request.headers.get("X-Request-ID", "N/A")
        }, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "Invalid input.",
                "data": serializer.errors,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            otp_token = OTPService.verify_otp(data['identifier'], data['code'], data['purpose'])
            if otp_token.user:
                otp_token.user.is_verified = True
                otp_token.user.save()

            return Response({
                "success": True,
                "code": "OTP_VERIFIED",
                "message": "OTP verified successfully.",
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                "success": False,
                "code": "OTP_VERIFICATION_FAILED",
                "message": str(e),
                "data": None,
                "request_id": request.headers.get("X-Request-ID", "N/A")
            }, status=status.HTTP_400_BAD_REQUEST)
