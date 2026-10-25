import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User, OTPToken
from apps.customers.models import CustomerProfile


@pytest.mark.django_db
class TestIdentityAndAuth:
    def test_customer_registration(self):
        client = APIClient()
        url = reverse('auth-register')
        payload = {
            "email": "testcustomer@brmfb.ng",
            "phone_number": "08012345678",
            "password": "SecurePassword123!",
            "first_name": "Amina",
            "last_name": "Borno",
            "address": "Maiduguri, Borno State"
        }
        response = client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'customer_number' in response.data['data']
        assert 'mock_otp' in response.data['data']

        user = User.objects.get(email="testcustomer@brmfb.ng")
        assert user.phone_number == "08012345678"
        assert not user.is_verified

        profile = CustomerProfile.objects.get(user=user)
        assert profile.first_name == "Amina"
        assert profile.kyc_status == 'PENDING'

    def test_customer_login_and_otp_verification(self):
        # Register user first
        user = User.objects.create_user(
            email="loginuser@brmfb.ng",
            phone_number="08087654321",
            password="SecurePassword123!"
        )
        CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB12345678",
            first_name="Modu",
            last_name="Lawan",
            phone="08087654321",
            email="loginuser@brmfb.ng"
        )

        client = APIClient()
        login_url = reverse('auth-login')
        payload = {
            "email": "loginuser@brmfb.ng",
            "password": "SecurePassword123!",
            "device_id": "device-uuid-999",
            "platform": "Android",
            "app_version": "1.0.0"
        }
        response = client.post(login_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'session_id' in response.data['data']
        assert 'refresh_token' in response.data['data']

        # Request OTP
        otp_request_url = reverse('otp-request')
        otp_payload = {
            "identifier": "loginuser@brmfb.ng",
            "purpose": "LOGIN"
        }
        otp_res = client.post(otp_request_url, otp_payload, format='json')
        assert otp_res.status_code == status.HTTP_200_OK
        mock_otp = otp_res.data['data']['mock_otp']

        # Verify OTP
        otp_verify_url = reverse('otp-verify')
        verify_payload = {
            "identifier": "loginuser@brmfb.ng",
            "code": mock_otp,
            "purpose": "LOGIN"
        }
        verify_res = client.post(otp_verify_url, verify_payload, format='json')
        assert verify_res.status_code == status.HTTP_200_OK
        assert verify_res.data['success'] is True

        user.refresh_from_db()
        assert user.is_verified
