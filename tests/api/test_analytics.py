import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.identity.models import User
from apps.customers.models import CustomerProfile


@pytest.mark.django_db
class TestAnalyticsSpendingTrends:
    def test_get_spending_trends(self):
        user = User.objects.create_user(
            email="analyticsuser@brmfb.ng",
            phone_number="08099887755",
            password="SecurePassword123!"
        )
        profile = CustomerProfile.objects.create(
            user=user,
            customer_number="BRMFB11112222",
            first_name="Fatima",
            last_name="Bello",
            phone="08099887755",
            email="analyticsuser@brmfb.ng"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('spending-trends')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'summary' in response.data['data']
        assert 'monthly_trends' in response.data['data']
        assert 'category_breakdown' in response.data['data']
        assert response.data['data']['summary']['currency'] == 'NGN'
