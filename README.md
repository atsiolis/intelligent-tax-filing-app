# TaxMind — Intelligent Tax Filing Assistant

A web application that provides AI-generated tax guidance based on user-submitted financial information. Built as part of the Deloitte AI Engineer Assessment (2026).

> **Scope:** This application is scoped to Greek tax law and AADE regulations.

---

## Project Structure

```
tax-filing-app/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── validation.js
│       ├── api.js
│       ├── ui.js
│       └── main.js
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.10+
- A modern web browser

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/atsiolis/intelligent-tax-filing-app.git
cd intelligent-tax-filing-app
```

### 2. Set up the backend

Navigate to the backend folder and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file from the example template:

```bash
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

Start the backend server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 3. Run the frontend

Open `frontend/index.html` directly in your browser. No build step or server required.

---

## API Documentation

FastAPI provides automatic interactive documentation. With the backend running, visit:

```
http://localhost:8000/docs
```

### Endpoints

#### `GET /`

Health check. Returns a confirmation that the API is running.

**Response:**
```json
{
  "message": "TaxMind API is running."
}
```

---

#### `POST /api/tax-advice`

Accepts tax form data and returns AI-generated advice.

**Request body:**

| Field | Type | Description |
|-------|------|-------------|
| `income` | float | Gross annual income in euros |
| `expenses` | float | Total deductible annual expenses in euros |
| `filingStatus` | string | One of: `single`, `married_joint`, `married_separate`, `head_of_household` |
| `dependents` | integer | Number of dependents (0 or more) |
| `employmentType` | string | One of: `employed`, `self_employed`, `freelancer`, `mixed` |

**Example request:**
```json
{
  "income": 50000,
  "expenses": 10000,
  "filingStatus": "single",
  "dependents": 0,
  "employmentType": "employed"
}
```

**Response:**
```json
{
  "advice": "Based on your submission..."
}
```

**Error responses:**

| Status | Reason |
|--------|--------|
| `400` | Invalid filing status or employment type |
| `400` | Negative income or expenses |
| `400` | Expenses exceed income |
| `400` | Negative number of dependents |
| `422` | Missing or malformed request fields |

---

## Frontend Overview

The frontend is built with plain HTML, CSS, and JavaScript — no frameworks or build tools required.

The JavaScript is split into four files, each with a single responsibility:

| File | Responsibility |
|------|---------------|
| `validation.js` | Collects and validates form data before submission |
| `api.js` | Handles communication with the backend, includes a mock response for development |
| `ui.js` | All DOM manipulation — showing and hiding elements |
| `main.js` | Entry point — sets up event listeners and coordinates the other modules |

### Development mode (no backend)

`api.js` includes a `USE_MOCK` flag at the top. When set to `true`, the frontend returns a mock response without needing the backend to be running. Set it to `false` to connect to the real backend.

```javascript
const USE_MOCK = true; // ← Set to false once backend is running
```

