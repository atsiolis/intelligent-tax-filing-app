// =============================================
//  api.js
//  Handles communication with the backend API.
//  USE_MOCK = true while backend is not running.
// =============================================

const API_URL = 'http://localhost:8000/api/tax-advice';
const USE_MOCK = false; // ← Set to false once backend is running

async function getAdvice(data) {
    return USE_MOCK
        ? await getMockAdvice(data)
        : await fetchAdviceFromBackend(data);
}

async function fetchAdviceFromBackend(data) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Server responded with status ${response.status}`);
    }

    const result = await response.json();
    return result.advice; // Expects { advice: "..." } from backend
}

// --- Mock response (no backend yet) ---
async function getMockAdvice(data) {
    await sleep(2000); // Simulate network delay

    const netIncome = data.income - data.expenses;
    const employmentLabel = formatEmploymentType(data.employmentType);
    const filingStatus = formatFilingStatus(data.filingStatus);

    return `Based on the information you provided, here is a preliminary overview of your tax situation:

You reported an annual income of €${formatCurrency(data.income)} with deductible expenses of €${formatCurrency(data.expenses)}, resulting in a net taxable income of approximately €${formatCurrency(netIncome)}.

As a ${employmentLabel} with a ${filingStatus} filing status and ${data.dependents} dependent(s), there are several key considerations:

1. Deductible Expenses: Your declared expenses of €${filingStatus} may reduce your taxable income, depending on their nature and AADE-approved categories.

2. Dependents: You may qualify for dependent-related tax credits or rebates, which could reduce your overall tax liability.

3. Employment Type: As a ${employmentLabel}, you should ensure that any advance income tax payments are up to date if applicable. Freelancers and self-employed individuals in Greece are generally required to pay advance tax (προκαταβολή φόρου) based on the prior year's income.

4. Next Steps: Consider consulting a registered tax accountant (λογιστής) to optimise deductions and ensure full compliance with current Greek tax legislation.

⚠ This is a mock response for development purposes. Connect the backend to receive real AI-generated advice.`;
}

// --- Utility ---
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function formatCurrency(value) {
    return Number(value).toLocaleString('el-GR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function formatEmploymentType(type) {
    const map = {
        employed: 'employed',
        self_employed: 'self-employed',
        freelancer: 'freelancer',
        mixed: 'someone with mixed income sources',
    };
    return map[type] || type;
}

function formatFilingStatus(status) {
    const map = {
        single: 'single',
        married_joint: 'married (filing jointly)',
        married_separate: 'married (filing separately)',
        head_of_household: 'head of household',
    };
    return map[status] || status;
}