# =============================================
#  main.py
#  FastAPI app entry point and routes.
# =============================================

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from models import TaxAdviceResponse, TaxFormData
from services.openai_service import get_advice

load_dotenv()

# --- Startup validation ---
if not os.getenv("OPENAI_API_KEY"):
    raise Exception("OPENAI_API_KEY environment variable not set. Please set it in .env.")

app = FastAPI(title="Eforion API", version="1.0.0")

# Create the limiter — identifies users by their IP address
limiter = Limiter(key_func=get_remote_address)

# Attach it to the FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- CORS ---
# Allows the frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://127.0.0.1:5500",  # VS Code Live Server
        "null"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Eforion API is running."}


@app.post("/api/tax-advice", response_model=TaxAdviceResponse)
@limiter.limit("5/minute")
async def get_tax_advice(request: Request, data: TaxFormData):
    
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

    return TaxAdviceResponse(advice=advice)