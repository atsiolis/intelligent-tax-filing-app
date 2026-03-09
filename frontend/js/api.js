// =============================================
//  api.js
//  Handles communication with the backend API
// =============================================

const API_URL = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === ''
)
    ? 'http://localhost:8000/api/tax-advice'
    : 'http://backend:8000/api/tax-advice';
const TIMEOUT_MS = 20000; // 20 seconds

async function getAdvice(data) {
    return await fetchAdviceFromBackend(data);
}

async function fetchAdviceFromBackend(data) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            signal: controller.signal,
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));

            const detail = errorBody.detail;
            const message = Array.isArray(detail)
                ? detail.map(e => e.msg).join('\n')
                : detail || `Server responded with status ${response.status}`;

            throw new Error(message);
        }

        const result = await response.json();
        return result.advice;

    } catch (err) {
        if (err.name === 'AbortError') {
            throw new Error('The request timed out. Please try again.');
        }
        throw err;
    } finally {
        clearTimeout(timeout);
    }
}