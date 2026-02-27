// =============================================
//  main.js
//  Entry point — sets up event listeners and
//  coordinates validation, API, and UI modules.
// =============================================

const form = document.getElementById('taxForm');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    // 1. Collect & validate
    const data = collectFormData();
    const validationError = validateFormData(data);

    if (validationError) {
        showError(validationError);
        return;
    }

    // 2. Update UI — show loading, hide old result
    showLoading(true);
    hideResult();
    setSubmitDisabled(true);

    try {
        // 3. Call API (real or mock)
        const advice = await getAdvice(data);

        // 4. Display result
        showResult(advice);

    } catch (err) {
        showError('Something went wrong. Please check that the backend is running and try again.');
        console.error('API Error:', err);

    } finally {
        showLoading(false);
        setSubmitDisabled(false);
    }
});

// Clear form also resets UI state
form.addEventListener('reset', () => {
    hideError();
    hideResult();
    showLoading(false);
});