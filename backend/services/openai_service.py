# =============================================
#  services/openai_service.py
#  Builds the prompt from the user's tax data
#  and calls the OpenAI API.
# =============================================

import os 
import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv
from fastapi import HTTPException
from models import TaxFormData

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_advice(data: TaxFormData) -> str:
    """
    Builds the prompt from the user's tax data
    and calls the OpenAI API.
    """
    
    prompt = build_prompt(data)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3, # Low temperature for consistent, factual advice
            max_tokens=800
        )
        return response.choices[0].message.content
    
    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key. Please check your .env file.")

    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit reached. Please try again shortly.")

    except openai.APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to OpenAI. Please check your internet connection.")

    except openai.APIStatusError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI returned an error: {e.message}")

    
    
    
    
def build_prompt(data: TaxFormData) -> str:
    """
    Builds the prompt from the user's tax data.
    """
    
    net_income = data.income - data.expenses
    
    filing_status_label = {
        "single": "single",
        "married_joint": "married (filing jointly)",
        "married_separate": "married (filing separately)",
        "head_of_household": "head of household",
    }
    
    employment_type_label = {
        "employed": "employed",
        "self_employed": "self-employed",
        "freelancer": "freelancer",
        "mixed": "someone with mixed income sources",
    }
    
    filing_status = filing_status_label[data.filingStatus]
    employment_type = employment_type_label[data.employmentType]
    
    return f"""Here is the tax profile for the individual you are advising:

- Gross annual income: €{data.income}
- Deductible expenses: €{data.expenses}
- Net taxable income: €{net_income}
- Filing status: {filing_status}
- Number of dependents: {data.dependents}
- Employment type: {employment_type}

Using this information, provide structured tax advice following this exact format:

1. Tax Situation Overview
Summarise their overall tax position based on the figures above.

2. Deductions and Credits
List the deductions or credits they may qualify for under Greek tax law given their profile.

3. Employment Obligations
Explain any tax obligations specific to their employment type.

4. Next Steps
Give 2 to 3 clear, actionable steps they should take.

End with a single sentence disclaimer that this is AI-generated guidance and they should consult a registered tax accountant for professional advice.

Keep the entire response under 350 words. Use plain text only — no markdown, no bold, no bullet symbols.
"""


SYSTEM_PROMPT = """You are a tax assistant specialising in Greek tax law and AADE regulations.

Your role is to give clear, practical, and accurate tax guidance based on the user's financial profile.

Rules:
- Base all advice on Greek tax law
- Speak in general terms — do not cite specific tax rates or figures as these change regularly
- Use plain language and avoid jargon
- Never use markdown formatting such as bold, headers, or bullet symbols — use plain numbered text only
- Always stay within the word limit given in the user prompt
"""