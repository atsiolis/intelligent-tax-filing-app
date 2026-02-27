# =============================================
#  models.py
#  Pydantic models for request and response
#  validation.
# =============================================

from pydantic import BaseModel


class TaxFormData(BaseModel):
    income: float
    expenses: float
    filingStatus: str
    dependents: int
    employmentType: str


class TaxAdviceResponse(BaseModel):
    advice: str
