# =============================================
#  models.py
#  Pydantic models for request and response
#  validation.
# =============================================

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class FilingStatus(str, Enum):
    single = "single"
    married_joint = "married_joint"
    married_separate = "married_separate"
    head_of_household = "head_of_household"


class EmploymentType(str, Enum):
    employed = "employed"
    self_employed = "self_employed"
    freelancer = "freelancer"
    mixed = "mixed"


class TaxFormData(BaseModel):
    income: float = Field(ge=0, le=10_000_000)
    expenses: float = Field(ge=0, le=10_000_000)
    filingStatus: FilingStatus
    dependents: int = Field(ge=0, le=20)
    employmentType: EmploymentType

    @model_validator(mode="after")
    def validate_expenses_vs_income(self):
        if self.expenses > self.income:
            raise ValueError("Expenses cannot exceed income.")
        return self
    

class TaxAdviceResponse(BaseModel):
    advice: str