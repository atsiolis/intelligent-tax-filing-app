# =============================================
#  tests/test_rate_limit.py
#  Tests for the rate limiting behaviour
#  on the /api/tax-advice endpoint.
# =============================================

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app, limiter

client = TestClient(app)

MOCK_ADVICE = "This is your tax advice."

VALID_PAYLOAD = {
    "income": 50000,
    "expenses": 10000,
    "filingStatus": "single",
    "dependents": 0,
    "employmentType": "employed",
}

@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield


@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_requests_within_limit_succeed():
    for _ in range(5):
        response = client.post(
            "/api/tax-advice",
            json=VALID_PAYLOAD,
            headers={"X-Forwarded-For": "1.2.3.4"},
        )
        assert response.status_code == 200


@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_sixth_request_is_blocked():
    for _ in range(5):
        client.post(
            "/api/tax-advice",
            json=VALID_PAYLOAD,
            headers={"X-Forwarded-For": "1.2.3.4"},
        )
    response = client.post(
        "/api/tax-advice",
        json=VALID_PAYLOAD,
        headers={"X-Forwarded-For": "1.2.3.4"},
    )
    assert response.status_code == 429
