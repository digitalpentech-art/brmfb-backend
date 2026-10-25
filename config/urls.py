from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.common.urls')),
    path('api/v1/auth/', include('apps.identity.urls')),
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/transactions/', include('apps.transactions.urls')),
    path('api/v1/beneficiaries/', include('apps.beneficiaries.urls')),
    path('api/v1/transfers/', include('apps.transfers.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/support/', include('apps.support.urls')),
]
