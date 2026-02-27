// =============================================
//  ui.js
//  All DOM manipulation and UI state functions.
//  No business logic here — only show/hide/render.
// =============================================

const submitBtn = document.getElementById('submitBtn');
const formError = document.getElementById('formError');
const formErrorMsg = document.getElementById('formErrorMsg');
const loadingCard = document.getElementById('loadingCard');
const resultCard = document.getElementById('resultCard');
const resultContent = document.getElementById('resultContent');

function showLoading(visible) {
    loadingCard.classList.toggle('hidden', !visible);
}

function showResult(advice) {
    resultContent.textContent = advice;
    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideResult() {
    resultCard.classList.add('hidden');
    resultContent.textContent = '';
}

function showError(message) {
    formErrorMsg.textContent = message;
    formError.classList.remove('hidden');
    formError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    formError.classList.add('hidden');
}

function setSubmitDisabled(disabled) {
    submitBtn.disabled = disabled;
}