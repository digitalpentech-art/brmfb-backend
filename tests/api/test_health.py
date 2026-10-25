import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHealthEndpoints:
    def test_liveness_check(self):
        client = APIClient()
        url = reverse('health-live')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'alive'
        assert response.data['service'] == 'brmfb-backend'

    def test_readiness_check(self):
        client = APIClient()
        url = reverse('health-ready')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ready'
        assert response.data['database'] == 'healthy'
