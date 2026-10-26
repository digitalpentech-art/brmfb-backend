from django.urls import path
from .views import SpendingTrendsView

urlpatterns = [
    path('spending-trends/', SpendingTrendsView.as_view(), name='spending-trends'),
]
