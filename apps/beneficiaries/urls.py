from django.urls import path
from .views import BeneficiaryListCreateView, BeneficiaryDetailView

urlpatterns = [
    path('', BeneficiaryListCreateView.as_view(), name='beneficiary-list-create'),
    path('<uuid:beneficiary_id>/', BeneficiaryDetailView.as_view(), name='beneficiary-detail'),
]
