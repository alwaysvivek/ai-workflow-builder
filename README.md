A Flask + React application that constructs and executes multi-step text processing workflows using LLMs (Groq/Llama 3).

## Features

- **Workflow Builder**: Design custom chains of actions (Clean, Summarize, Simplify, Analyze, etc.).
- **Real-Time Streaming Capability**: Backend supports NDJSON streaming (Newline Delimited JSON) for watching the AI process each step in real-time. (Note: Frontend currently defaults to Sync for maximum reliability).
- **Resilient**: Automatic retries for empty LLM responses and robust error handling.
- **Secure**: BYOK (Bring Your Own Key) architecture — API keys are never stored permanently, only validated. Input sanitization prevents XSS.
- **Traceable**: Full run history stored in SQLite. structured JSON logging for observability.

## Architecture

- **Backend**: Python 3.12+, Flask, SQLAlchemy, SQLite.
    - `blueprints/`: Route definitions.
    - `core/`: Business logic, LLM service, Sanitization.
    - **No complexity**: Flat structure where possible.
- **Frontend**: React, Vite, TailwindCSS.
    - `src/api.js`: Single API client entry point.
    - `src/components/`, `src/pages/`: UI logic.
    - **Design Philosophy**: Intentionally utilitarian. We avoided complex UI libraries or "shiny" aesthetics to focus on a clean, understandable codebase that serves as a test harness for the backend architecture.
- **Database**: SQLite (file-based).
    - Simple file-based storage, perfect for this assessment scope.

## Quick Start (Docker)

The easiest way to run the application is with Docker Compose.

1. **Prerequisites**: Docker and Docker Compose installed.
2. **Setup**: Create a `.env` file in the root directory to pre-fill your API key:
   ```bash
   echo "GROQ_API_KEY=gsk_your_actual_key_here" > .env
   ```
3. **Run**:
   ```bash
   docker-compose up --build
   ```
4. **Access**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:5001](http://localhost:5001)


## Quick Start (Local Dev)

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Checks: `http://localhost:5001/api/health`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Access: `http://localhost:5173`

## Technical API Reference

The backend exposes a REST API (prefixed with `/api`) to support the unified React frontend and external observability. A full **OpenAPI Specification** is available in [openapi.json](./openapi.json).

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | System health check (Database connectivity). |
| `/api/validate-key` | `POST` | Validates a Groq API Key against the upstream provider. |
| `/api/workflows` | `POST` | Creates a new workflow template. |
| `/api/workflows/run/sync` | `POST` | Executes a workflow synchronously with Pydantic validation. |
| `/api/runs` | `GET` | Retrieves the latest workflow execution history. |

## Extension Approach
The system is designed to be easily extensible without modifying core logic:
- **Adding New Actions**: Define a new `ActionType` enum in `backend/core/prompts.py` and add a corresponding Python string template. No other backend changes are needed.
- **Switching LLMs**: The `LLMService` class is isolated. Replace the Groq client implementation with OpenAI or Anthropic SDKs in `backend/services/llm.py`.
- **New Databases**: Change the `DATABASE_URL` environment variable. SQLAlchemy models are dialect-agnostic.

## Trade-offs & Decisions

### SQLite vs PostgreSQL
I chose **SQLite** for this submission to ensure the project is "self-contained" and easy to run without setting up a heavy DB container. For a production app with high concurrency, I would switch to PostgreSQL (the code is already using SQLAlchemy, so this switch is trivial).

### Flask vs FastAPI
The assessment requested Flask. To keep the execution logic lean and predictable, I used standard **Python String Formatting** (.format) for managing LLM prompts, ensuring low overhead and high readability.

### Security
- **Inputs**: All text inputs are sanitized (HTML stripped) before processing.
- **API Keys**: Groq API keys are passed via headers (`x-groq-api-key`) and validated against the Groq API before use. They are not stored in the database.
- **CORS**: Configured to allow traffic from any origin (`*`) to simplify local testing and assessment review. In a real production environment, this would be restricted to the frontend domain.

### Dependencies
Dependencies in `requirements.txt` are **strictly pinned** (e.g., `Flask==3.1.2`) to ensure 100% reproducibility across different reviewer environments.

## Engineering Weaknesses & Scale Path

In the spirit of "Communication" and "Trade-offs," here are the known weaknesses of the current implementation and how they would be addressed in a production environment:

1.  **SQLite Concurrency**: SQLite is not suitable for high-concurrency writes.
    -   *Scale Path*: Use **PostgreSQL** in production. The code uses SQLAlchemy, so this is an environment variable change away.
2.  **Synchronous Processing**: Workflow execution currently blocks the Flask worker. For long-running chains, this will lead to timeouts.
    -   *Scale Path*: Offload execution to **Celery/Redis** workers and use WebSockets or polling to notify the frontend of completion.
3.  **In-Memory Rate Limiting**: Limiters are currently in-memory and will reset on container restart.
    -   *Scale Path*: Use a persistent **Redis** store for `Flask-Limiter`.
4.  **Sync-over-Stream**: I intentionally chose atomic Pydantic validation over byte-by-byte streaming for this assessment to prioritize **Correctness** and **Simplicity**.
    -   *Scale Path*: Implement iterative JSON parsing (e.g., `ijson`) to support true partial streaming if "real-time" feel becomes the primary product requirement.

## Testing

Backend tests are written with `pytest`:
```bash
cd backend
python3 -m pytest
```

---

## Engineering Rigor

This system was intentionally designed to stay understandable and correct as it evolves:

- Clear boundaries: Flask blueprints isolate routing; core/ contains all business logic.

- Strong interfaces: All external inputs and LLM outputs are validated with Pydantic to prevent invalid states.

- Change resilience: Enum-driven action types and SQLAlchemy abstractions ensure new features don’t cause widespread impact.

- Observability by default: Structured JSON logs, run history, and a health endpoint make failures diagnosable.

- Constrained AI usage: AI assistance was guided by explicit rules (ai_guidance/) and all generated code was reviewed and hardened.
