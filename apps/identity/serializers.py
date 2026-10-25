from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from apps.customers.models import CustomerProfile


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=10)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    device_id = serializers.CharField(max_length=255)
    platform = serializers.CharField(max_length=50)
    app_version = serializers.CharField(max_length=50, required=False, allow_blank=True)


class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    purpose = serializers.ChoiceField(choices=[
        ('LOGIN', 'Login Verification'),
        ('REGISTRATION', 'Registration Verification'),
        ('TRANSFER', 'Transfer Authorization'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PIN_RESET', 'PIN Reset'),
    ])


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=10)
    purpose = serializers.ChoiceField(choices=[
        ('LOGIN', 'Login Verification'),
        ('REGISTRATION', 'Registration Verification'),
        ('TRANSFER', 'Transfer Authorization'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PIN_RESET', 'PIN Reset'),
    ])
