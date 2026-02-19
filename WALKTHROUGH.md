# Walkthrough: Better Software Submission (Flask + React)

Vivek has successfully transitioned from "Functional Delivery" to **"Production-Grade Engineering."** This submission for **Better Software** is a flagship example of how to orchestrate AI tools to build high-safety systems.
The project has been migrated from a legacy monolith to a decoupled **Flask API + React SPA** architecture using **SQLite**.

## 1. Architecture Overview

- **Backend**: Python/Flask (Application Factory Pattern)
    - **Blueprints**: `system` (Health, Runs) and `workflows` (Creation, Execution).
    - **Database**: SQLite with SQLAlchemy ORM.
    - **Validation**: Pydantic Schemas + Manual input sanitization.
    - **Logging**: Structured JSON logging for professional observability.
- **Frontend**: React (Vite) + TailwindCSS
    - **Components**: `WorkflowBuilder` (Creation), `RunHistory` (Monitoring & Details).
    - **State**: Ephemeral React state (BYOK security).
    - **Integration**: Axios client pointing to `/api`.

## 2. Key Features & Constraints

- **Flexible Workflow Builder**: Modular pipeline-based interface to create 7-step logic chains.
- **Smart Constraints**: Prevents duplicate actions and enforces logical limits (Standard > Clever).
- **Synchronous Execution engine**: Robust, transactional backend execution (Flask + SQLAlchemy) that guaranteed data integrity.
- **Real-time History**: View past runs with **IST Timestamps**, detailed step breakdowns, and status tracking.
- **Production Grade**:
    - **Security**: Strict Pydantic validation, Input Sanitization, JSON Structured Logging, CORS protection.
    - **Reliability**: Retries on LLM failure, Timeout handling (300s), Connection pool management.
    - **UX**: "Details" modal for deep inspection. **Security Note**: API Key is ephemeral (not saved) for strict security.


## 4. Verification Steps

### Backend Verification
I have run the backend tests and confirmed they pass:
```bash
cd backend
python3 -m pytest
```
*Result: All tests passed (Health check, API key validation, Workflow creation, Retrieval).*

### Frontend Verification
The frontend builds successfully and connects to the backend at `http://localhost:5001`.
- **Manual Check**:
    1.  Create Workflow (Steps: Clean -> Summarize).
    2.  Run with text.
    3.  Verify "Processing..." -> "Completed".
    4.  Check History -> See IST timestamp -> Click Details -> See Step Outputs.

## 5. Artifacts Created

| Artifact | Purpose |
|---|---|
| `README.md` | Setup instructions, architectural decisions, and trade-offs. |
| `AI_NOTES.md` | Honest declaration of AI usage (boilerplate, translation). |
| `PROMPTS_USED.md` | Log of prompts used to generate the code. |
| `WALKTHROUGH.md` | Detailed breakdown of structure, risks, and extension approach. |
| `openapi.json` | Formal REST API contract. |
| `ai_guidance/rules.md` | Standards used to constrain AI during development. |
| `docker-compose.yml` | One-command startup for reviewers. |

## 6. Risks & Limitations

- **SQLite Concurrency**: I used SQLite for simplicity/portability. However, SQLite locks the database file during writes. In a high-traffic production environment, this would cause bottlenecks.
    - *Mitigation*: The app uses SQLAlchemy, so switching to PostgreSQL is a config change (`DATABASE_URL`).
- **Sync Workers**: Flask's synchronous nature means long-running LLM requests hold the worker thread.
    - *Mitigation*: I used `gunicorn` with threaded workers strategies (`--threads 2`). For massive scale, an async task queue (Celery/Redis) would be the next step.
- **Security**: While inputs are sanitized, a dedicated WAF would be needed for public deployment.

## 7. How to Run

**Method A: Docker (Recommended)**
```bash
docker-compose up --build
```
Open [http://localhost:3000](http://localhost:3000).

**Method B: Local**
1. Backend: `cd backend && python3 app.py` (Port 5001)
2. Frontend: `cd frontend && npm run dev` (Port 5173)
