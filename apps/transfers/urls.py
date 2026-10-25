from django.urls import path
from .views import AccountVerificationView, TransferExecuteView

urlpatterns = [
    path('verify-account/', AccountVerificationView.as_view(), name='account-verify'),
    path('', TransferExecuteView.as_view(), name='transfer-execute'),
]
