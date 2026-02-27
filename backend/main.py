# =============================================
#  main.py
#  FastAPI app entry point and routes.
# =============================================

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TaxFormData, TaxAdviceResponse
from dotenv import load_dotenv
from services.openai_service import get_advice

load_dotenv()

# --- Startup validation ---
if not os.getenv("OPENAI_API_KEY"):
    raise Exception("OPENAI_API_KEY environment variable not set. Please set it in .env.")


app = FastAPI(title="Eforion API", version="1.0.0")

# --- CORS ---
# Allows the frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with the frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Eforion API is running."}


@app.post("/api/tax-advice", response_model=TaxAdviceResponse)
async def get_tax_advice(data: TaxFormData):
    
    """
    Receives tax form data from the frontend
    and returns AI-generated tax advice.
    """

    valid_filing_statuses = {"single", "married_joint", "married_separate", "head_of_household"}
    valid_employment_types = {"employed", "self_employed", "freelancer", "mixed"}

    if data.filingStatus not in valid_filing_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid filing status. Must be one of: {', '.join(valid_filing_statuses)}")

    if data.employmentType not in valid_employment_types:
        raise HTTPException(status_code=400, detail=f"Invalid employment type. Must be one of: {', '.join(valid_employment_types)}")

    if data.income < 0 or data.expenses < 0:
        raise HTTPException(status_code=400, detail="Income and expenses must be non-negative.")

    if data.expenses > data.income:
        raise HTTPException(status_code=400, detail="Expenses cannot exceed income.")
    
    if data.dependents < 0:
        raise HTTPException(status_code=400, detail="Dependents must be non-negative.")

    advice = await get_advice(data)

    # # --- Hardcoded response (will be replaced) ---
    # advice = (
    #     f"Based on your submission, your net taxable income is approximately "
    #     f"€{net_income} after deducting expenses of €{data.expenses} "
    #     f"from your gross income of €{data.income}.\n\n"
    #     f"As a {data.employmentType.replace('_', '-')} individual filing as "
    #     f"{data.filingStatus.replace('_', ' ')} with {data.dependents} dependent(s), "
    #     f"you may be eligible for various deductions and credits under Greek tax law.\n\n"
    #     f"This is a placeholder response. AI-generated advice will appear here in Step 3."
    # )

    return TaxAdviceResponse(advice=advice)