# =============================================
#  tests/test_openai_service.py
#  Tests for openai_service.py directly —
#  covers build_prompt() and the error
#  handling branches in get_advice().
# =============================================

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from models import TaxFormData
from services.openai_service import build_prompt, get_advice


# ── Shared test data ─────────────────────────────────────────────

VALID_DATA = TaxFormData(
    income=50000,
    expenses=10000,
    filingStatus="single",
    dependents=0,
    employmentType="employed",
)

# ── Helpers ──────────────────────────────────────────────────────

def make_openai_response(content: str):
    """
    Builds a minimal mock that looks like an OpenAI chat completion
    response. Only the fields our code actually reads are needed.
    """
    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response

# ════════════════════════════════════════════════════════════════
# build_prompt() tests
# ════════════════════════════════════════════════════════════════

class TestBuildPrompt:

    def test_contains_income(self):
        prompt = build_prompt(VALID_DATA)
        assert "50000" in prompt

    def test_contains_expenses(self):
        prompt = build_prompt(VALID_DATA)
        assert "10000" in prompt

    def test_calculates_net_income(self):
        # net = income - expenses = 50000 - 10000 = 40000
        prompt = build_prompt(VALID_DATA)
        assert "40000" in prompt

    def test_filing_status_label_single(self):
        prompt = build_prompt(VALID_DATA)
        assert "single" in prompt

    def test_filing_status_label_married_joint(self):
        data = VALID_DATA.model_copy(update={"filingStatus": "married_joint"})
        prompt = build_prompt(data)
        assert "married (filing jointly)" in prompt

    def test_filing_status_label_married_separate(self):
        data = VALID_DATA.model_copy(update={"filingStatus": "married_separate"})
        prompt = build_prompt(data)
        assert "married (filing separately)" in prompt

    def test_filing_status_label_head_of_household(self):
        data = VALID_DATA.model_copy(update={"filingStatus": "head_of_household"})
        prompt = build_prompt(data)
        assert "head of household" in prompt

    def test_employment_type_label_employed(self):
        prompt = build_prompt(VALID_DATA)
        assert "employed" in prompt

    def test_employment_type_label_self_employed(self):
        data = VALID_DATA.model_copy(update={"employmentType": "self_employed"})
        prompt = build_prompt(data)
        assert "self-employed" in prompt

    def test_employment_type_label_freelancer(self):
        data = VALID_DATA.model_copy(update={"employmentType": "freelancer"})
        prompt = build_prompt(data)
        assert "freelancer" in prompt

    def test_employment_type_label_mixed(self):
        data = VALID_DATA.model_copy(update={"employmentType": "mixed"})
        prompt = build_prompt(data)
        assert "mixed income" in prompt

    def test_contains_dependents(self):
        data = VALID_DATA.model_copy(update={"dependents": 3})
        prompt = build_prompt(data)
        assert "3" in prompt

    def test_prompt_is_string(self):
        prompt = build_prompt(VALID_DATA)
        assert isinstance(prompt, str)

    def test_prompt_is_not_empty(self):
        prompt = build_prompt(VALID_DATA)
        assert len(prompt) > 0

    def test_prompt_contains_four_sections(self):
        prompt = build_prompt(VALID_DATA)
        assert "1. Tax Situation Overview" in prompt
        assert "2. Deductions and Credits" in prompt
        assert "3. Employment Obligations" in prompt
        assert "4. Next Steps" in prompt

    def test_prompt_requests_plain_text(self):
        prompt = build_prompt(VALID_DATA)
        assert "plain text" in prompt.lower()

    def test_prompt_requests_disclaimer(self):
        prompt = build_prompt(VALID_DATA)
        assert "disclaimer" in prompt.lower()

    def test_zero_expenses_net_income_equals_income(self):
        data = VALID_DATA.model_copy(update={"expenses": 0})
        prompt = build_prompt(data)
        # net income = 50000 - 0 = 50000, should appear twice
        assert prompt.count("50000") >= 2

# ════════════════════════════════════════════════════════════════
# get_advice() tests — happy path
# ════════════════════════════════════════════════════════════════

class TestGetAdviceSuccess:

    @pytest.mark.asyncio
    async def test_returns_content_from_openai(self):
        mock_response = make_openai_response("This is tax advice.")
        with patch("services.openai_service.client.chat.completions.create", AsyncMock(return_value=mock_response)):
            result = await get_advice(VALID_DATA)
        assert result == "This is tax advice."
        
    @pytest.mark.asyncio
    async def test_passes_correct_model(self):
        mock_response = make_openai_response("advice")
        with patch("services.openai_service.client.chat.completions.create", AsyncMock(return_value=mock_response)) as mock_create:
            await get_advice(VALID_DATA)
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o-mini"
        
    @pytest.mark.asyncio
    async def test_passes_correct_temperature(self):
        mock_response = make_openai_response("advice")
        with patch("services.openai_service.client.chat.completions.create", AsyncMock(return_value=mock_response)) as mock_create:
            await get_advice(VALID_DATA)
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.3
        
    @pytest.mark.asyncio
    async def test_passes_correct_max_tokens(self):
        mock_response = make_openai_response("advice")
        with patch("services.openai_service.client.chat.completions.create", AsyncMock(return_value=mock_response)) as mock_create:
            await get_advice(VALID_DATA)
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 800
        
    @pytest.mark.asyncio
    async def test_passes_system_and_user_messages(self):
        mock_response = make_openai_response("advice")
        with patch("services.openai_service.client.chat.completions.create", AsyncMock(return_value=mock_response)) as mock_create:
            await get_advice(VALID_DATA)
        call_kwargs = mock_create.call_args.kwargs
        roles = [msg["role"] for msg in call_kwargs["messages"]]
        assert "system" in roles
        assert "user" in roles
        
# ════════════════════════════════════════════════════════════════
# get_advice() tests — error handling
# ════════════════════════════════════════════════════════════════

class TestGetAdviceErrorHandling:
    
    @pytest.mark.asyncio
    async def test_authentication_error_raises_401(self):
        import openai
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.headers = {}
        exc = openai.AuthenticationError(
            message="Invalid API key",
            response=mock_response,
            body={"error": {"message": "Invalid API key"}},
        )
        with patch("services.openai_service.client.chat.completions.create",AsyncMock(side_effect=exc)):
            with pytest.raises(HTTPException) as raised:
                await get_advice(VALID_DATA)
        assert raised.value.status_code == 401
        assert "api key" in raised.value.detail.lower()
        
    @pytest.mark.asyncio
    async def test_rate_limit_error_raises_429(self):
        import openai
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        exc = openai.RateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}},
        )
        with patch("services.openai_service.client.chat.completions.create",AsyncMock(side_effect=exc)):
            with pytest.raises(HTTPException) as raised:
                await get_advice(VALID_DATA)
        assert raised.value.status_code == 429
        assert "rate limit" in raised.value.detail.lower()
        
    @pytest.mark.asyncio
    async def test_connection_error_raises_503(self):
        import openai
        exc = openai.APIConnectionError(request=MagicMock())
        with patch("services.openai_service.client.chat.completions.create",AsyncMock(side_effect=exc)):
            with pytest.raises(HTTPException) as raised:
                await get_advice(VALID_DATA)
        assert raised.value.status_code == 503
        assert "connect" in raised.value.detail.lower()
        
    @pytest.mark.asyncio
    async def test_api_status_error_raises_502(self):
        import openai
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        exc = openai.APIStatusError(
            message="Internal server error",
            response=mock_response,
            body={"error": {"message": "Internal server error"}},
        )
        with patch("services.openai_service.client.chat.completions.create",AsyncMock(side_effect=exc)):
            with pytest.raises(HTTPException) as raised:
                await get_advice(VALID_DATA)
        assert raised.value.status_code == 502
        assert "openai" in raised.value.detail.lower()
        
