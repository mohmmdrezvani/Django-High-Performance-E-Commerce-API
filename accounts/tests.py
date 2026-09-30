import pytest

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient


# Create your tests here.
@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAuthOTP:
    def test_send_otp_success(self, api_client):
        url = reverse('send_otp')
        payload = {'phone_number': '09014862969'}
        response = api_client.post(url, api_client)

        assert response.status_code == 200
        cached_code = cache.get('otp:09014862969')
        assert cached_code is not None
        assert len(cached_code) == 5

    def test_send_otp_invalid_phone(self, api_client):
        url = reverse('send_otp')
        payload = {'phone_number': '123456'}
        response = api_client.post(url, payload)

        assert response.status_code == 400

    def test_verify_otp_success(self, api_client):
        phone = '09014862969'
        cache.set(f"otp:{phone} , 12345", timeout=120)

        url = reverse('verify_otp')
        payload = {'phone_number': phone, 'code': '12345'}
        response = api_client.post(url, api_client)

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert cache.get(f'otp:{phone}') is  None
