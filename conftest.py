import pytest
from django.urls import reverse

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()