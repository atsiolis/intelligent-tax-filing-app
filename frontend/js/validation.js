// =============================================
//  validation.js
//  Collects form data and validates inputs
//  before submission.
// =============================================

function collectFormData() {
    const employmentTypeEl = document.querySelector('input[name="employmentType"]:checked');

    return {
        income: parseFloat(document.getElementById('income').value) || null,
        expenses: parseFloat(document.getElementById('expenses').value) || null,
        filingStatus: document.getElementById('filingStatus').value || null,
        dependents: parseInt(document.getElementById('dependents').value, 10),
        employmentType: employmentTypeEl ? employmentTypeEl.value : null,
    };
}

function validateFormData(data) {
    if (data.income === null || isNaN(data.income) || data.income < 0) {
        return 'Please enter a valid annual income (must be 0 or greater).';
    }
    if (data.expenses === null || isNaN(data.expenses) || data.expenses < 0) {
        return 'Please enter a valid expenses amount (must be 0 or greater).';
    }
    if (!data.filingStatus) {
        return 'Please select your filing status.';
    }
    if (isNaN(data.dependents) || data.dependents < 0) {
        return 'Please enter a valid number of dependents (0 or more).';
    }
    if (!data.employmentType) {
        return 'Please select your employment type.';
    }
    return null; // No errors
}