from django.contrib import admin
from .models import User, Device, DeviceSession, OTPToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'is_active', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'phone_number')
    list_filter = ('is_active', 'is_verified', 'is_staff')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'device_id', 'is_active', 'created_at')
    search_fields = ('device_id', 'user__email')

@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'ip_address', 'is_active', 'expires_at', 'created_at')
    search_fields = ('user__email', 'ip_address')

@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'purpose', 'attempts', 'is_used', 'expires_at', 'created_at')
    search_fields = ('identifier',)
    list_filter = ('purpose', 'is_used')
