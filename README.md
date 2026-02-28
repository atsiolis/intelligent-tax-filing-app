# Eforion — Intelligent Tax Filing Assistant

A web application that provides AI-generated tax guidance based on user-submitted financial information.

> **Scope:** This application is scoped to Greek tax law and AADE regulations.

---

## Project Structure

```
intelligent-tax-filing-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── validation.js
│       ├── api.js
│       ├── ui.js
│       └── main.js
├── backend/
│   ├── services/
│   │   ├── __init__.py
│   │   └── openai_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_main.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env.example
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

- Python 3.10+
- A modern web browser
- An OpenAI API key
- Docker Desktop (for containerised setup)

---

## Getting Started

### Option 1 — Run with Docker (recommended)

Make sure Docker Desktop is running, then from the root of the project:

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

Build and start both containers:

```bash
docker-compose up --build
```

The application will be available at `http://localhost`.

---

### Option 2 — Run locally

#### 1. Clone the repository

```bash
git clone https://github.com/atsiolis/intelligent-tax-filing-app.git
cd intelligent-tax-filing-app
```

#### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
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

#### 3. Run the frontend

Open `frontend/index.html` directly in your browser. No build step or server required.

---

## Running Tests

From inside the `backend/` folder:

```bash
pytest tests/ -v
```

The tests mock the OpenAI API so no API key is required to run them.

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
  "message": "Eforion API is running."
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
  "advice": "1. Tax Situation Overview\n..."
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
| `api.js` | Handles communication with the backend |
| `ui.js` | All DOM manipulation — showing and hiding elements |
| `main.js` | Entry point — sets up event listeners and coordinates the other modules |

---

## AI Integration

The AI integration is handled in `backend/services/openai_service.py`.

When the user submits the form, the frontend sends the tax data to the `/api/tax-advice` endpoint. The backend builds a structured prompt from the data and sends it to the OpenAI API using the `gpt-4o-mini` model. The response is returned to the frontend and displayed in the result card.

### Prompt Design

The prompt instructs the model to return advice in four sections:

1. **Tax Situation Overview** — a summary of the user's tax position
2. **Deductions and Credits** — relevant deductions under Greek tax law
3. **Employment Obligations** — obligations specific to their employment type
4. **Next Steps** — 2 to 3 actionable steps

The system prompt enforces plain text output (no markdown), general language without specific tax figures, and a disclaimer at the end of every response.

### Model Settings

| Setting | Value | Reason |
|---------|-------|--------|
| Model | `gpt-4o-mini` | Cost-efficient, fast, sufficient for structured advice |
| Temperature | `0.3` | Low creativity for consistent, factual responses |
| Max tokens | `800` | Enough headroom to avoid responses being cut off |

---

## Docker

The application is fully containerised using Docker.

| File | Description |
|------|-------------|
| `Dockerfile.backend` | Packages the FastAPI backend using Python 3.12 slim |
| `Dockerfile.frontend` | Serves the static frontend files using Nginx |
| `docker-compose.yml` | Runs both containers together |

To stop the containers:

```bash
docker-compose down
```

---

## CI/CD

A GitHub Actions pipeline is configured in `.github/workflows/ci.yml`.

The pipeline runs automatically on every push to `main` and on every pull request targeting `main`. It performs the following steps:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs backend dependencies
4. Runs the full test suite with `pytest tests/ -v`

If any test fails the pipeline fails, preventing broken code from being merged into `main`.
