from django.urls import path
from .views import AirtimePaymentView, DataPaymentView, BillPaymentView, QRPaymentView

urlpatterns = [
    path('airtime/', AirtimePaymentView.as_view(), name='payment-airtime'),
    path('data/', DataPaymentView.as_view(), name='payment-data'),
    path('bills/', BillPaymentView.as_view(), name='payment-bills'),
    path('qr/', QRPaymentView.as_view(), name='payment-qr'),
]
