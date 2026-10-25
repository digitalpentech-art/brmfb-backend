import random
import string
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from .models import User, OTPToken, Device, DeviceSession
from apps.customers.models import CustomerProfile


class OTPService:
    @staticmethod
    def generate_otp(user, identifier, purpose, expiry_minutes=10):
        # In production, send via SMS/Email provider. For mock/dev, return or log.
        code = ''.join(random.choices(string.digits, k=6))
        code_hash = make_password(code)
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        # Invalidate any existing unused OTPs for this user/identifier & purpose
        OTPToken.objects.filter(
            identifier=identifier,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)

        otp_token = OTPToken.objects.create(
            user=user,
            identifier=identifier,
            code_hash=code_hash,
            purpose=purpose,
            expires_at=expires_at,
            max_attempts=3
        )
        return code, otp_token  # Return plain code for dev/testing mock

    @staticmethod
    def verify_otp(identifier, code, purpose):
        try:
            otp_token = OTPToken.objects.filter(
                identifier=identifier,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
        except OTPToken.DoesNotExist:
            raise ValidationError("Invalid or expired OTP code.")

        if otp_token.attempts >= otp_token.max_attempts:
            otp_token.is_used = True
            otp_token.save()
            raise ValidationError("Maximum OTP verification attempts exceeded.")

        otp_token.attempts += 1
        otp_token.save()

        if not check_password(code, otp_token.code_hash):
            remaining = otp_token.max_attempts - otp_token.attempts
            raise ValidationError(f"Invalid OTP code. {remaining} attempts remaining.")

        otp_token.is_used = True
        otp_token.save()
        return otp_token


class IdentityService:
    @staticmethod
    def register_customer(email, phone_number, password, first_name, last_name, date_of_birth=None, address=None):
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists.")
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("User with this phone number already exists.")

        user = User.objects.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
            is_verified=False
        )

        customer_number = f"BRMFB{random.randint(10000000, 99999999)}"
        while CustomerProfile.objects.filter(customer_number=customer_number).exists():
            customer_number = f"BRMFB{random.randint(10000000, 99999999)}"

        profile = CustomerProfile.objects.create(
            user=user,
            customer_number=customer_number,
            first_name=first_name,
            last_name=last_name,
            phone=phone_number,
            email=email,
            date_of_birth=date_of_birth,
            address=address,
            kyc_status='PENDING',
            account_status='ACTIVE'
        )

        return user, profile

    @staticmethod
    def create_session(user, device_id, platform, app_version, ip_address, user_agent):
        device, _ = Device.objects.get_or_create(
            device_id=device_id,
            defaults={
                'user': user,
                'platform': platform,
                'app_version': app_version,
            }
        )
        device.user = user
        device.platform = platform
        device.app_version = app_version
        device.last_active_at = timezone.now()
        device.save()

        refresh_token_raw = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        refresh_token_hash = make_password(refresh_token_raw)
        expires_at = timezone.now() + timedelta(days=7)

        session = DeviceSession.objects.create(
            device=device,
            user=user,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        return session, refresh_token_raw
