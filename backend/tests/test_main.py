# =============================================
#  tests/test_main.py
#  Tests for the /api/tax-advice endpoint.
#  The OpenAI call is mocked so tests run
#  without a real API key.
# =============================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app, limiter

@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield

client = TestClient(app)

# --- Valid base payload reused across tests ---
VALID_PAYLOAD = {
    "income": 50000,
    "expenses": 10000,
    "filingStatus": "single",
    "dependents": 0,
    "employmentType": "employed",
}

MOCK_ADVICE = "This is mock AI-generated tax advice."


# =============================================
#  Health Check
# =============================================


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Eforion API is running."}
    
    
# =============================================
#  Valid Requests
# =============================================


@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_valid_request():
    response = client.post("/api/tax-advice", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json() == {"advice": MOCK_ADVICE}
    
    
@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_valid_request_with_filing_status():
    statuses = ["single", "married_joint", "married_separate", "head_of_household"]
    for status in statuses:
        payload = VALID_PAYLOAD.copy()
        payload["filingStatus"] = status
        response = client.post("/api/tax-advice", json=payload)
        assert response.status_code == 200
        assert response.json() == {"advice": MOCK_ADVICE}
        
        
@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_valid_request_with_employment_type():
    employment_types = ["employed", "self_employed", "freelancer", "mixed"]
    for employment_type in employment_types:
        payload = VALID_PAYLOAD.copy()
        payload["employmentType"] = employment_type
        response = client.post("/api/tax-advice", json=payload)
        assert response.status_code == 200
        assert response.json() == {"advice": MOCK_ADVICE}
        

@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_zero_expenses():
    payload = VALID_PAYLOAD.copy()
    payload["expenses"] = 0
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 200
    assert response.json() == {"advice": MOCK_ADVICE}
 
    
@patch("main.get_advice", AsyncMock(return_value=MOCK_ADVICE))
def test_valid_dependents():
    payload = VALID_PAYLOAD.copy()
    payload["dependents"] = 1
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 200
    assert response.json() == {"advice": MOCK_ADVICE}
    
    
# =============================================
#  Invalid Filing Status
# =============================================


def test_invalid_filing_status():
    payload = VALID_PAYLOAD.copy()
    payload["filingStatus"] = "invalid"
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400
    assert "filing status" in response.json()["detail"].lower() 
    
    
# =============================================
#  Invalid Employment Type
# =============================================


def test_invalid_employment_type():
    payload = VALID_PAYLOAD.copy()
    payload["employmentType"] = "invalid"
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400
    assert "employment type" in response.json()["detail"].lower()
    

# =============================================
#  Invalid Income and Expenses
# =============================================


def test_negative_income():
    payload = VALID_PAYLOAD.copy()
    payload["income"] = -1
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400
    assert "non-negative" in response.json()["detail"].lower()
    
    
def test_negative_expenses():
    payload = VALID_PAYLOAD.copy()
    payload["expenses"] = -1
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400
    assert "non-negative" in response.json()["detail"].lower()
    
    
def test_expenses_exceed_income():
    payload = VALID_PAYLOAD.copy()
    payload["expenses"] = 60000
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400
    assert "exceed income" in response.json()["detail"].lower()
    
    
# =============================================
#  Invalid Dependents
# =============================================


def test_invalid_dependents():
    payload = VALID_PAYLOAD.copy()
    payload["dependents"] = -1
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 400  
    assert "non-negative" in response.json()["detail"].lower()
    

# =============================================
#  Missing Required Fields
# =============================================


def test_missing_income():
    payload = VALID_PAYLOAD.copy()
    payload.pop("income")
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 422
    

def test_missing_expenses():
    payload = VALID_PAYLOAD.copy()
    payload.pop("expenses")
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 422
    
    
def test_missing_filing_status():
    payload = VALID_PAYLOAD.copy()
    payload.pop("filingStatus")
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 422
    
    
def test_missing_dependents():
    payload = VALID_PAYLOAD.copy()
    payload.pop("dependents")
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 422


def test_missing_employment_type():
    payload = VALID_PAYLOAD.copy()
    payload.pop("employmentType")
    response = client.post("/api/tax-advice", json=payload)
    assert response.status_code == 422
    

def test_empty_body():
    response = client.post("/api/tax-advice", json={})
    assert response.status_code == 422