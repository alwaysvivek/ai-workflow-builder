# AI Guidance: Coding Standards & Constraints

This project was developed with a "Human-in-the-Loop" AI strategy. These are the rules used to constrain the AI agent's behavior and protect the system's integrity.

## 1. Architectural Boundaries
- **Flask Factory Pattern**: Always use `create_app`. Do NOT put database initialization or blueprint registration in the global scope.
- **Blueprint Isolation**: Keep routes in `blueprints/`. Keep business logic/AI prompting in `core/`.
- **Extension Singletons**: All Flask extensions (SQLAlchemy, Limiter) must be initialized in `extensions.py` to prevent circular imports.
- **BYOK (Bring Your Own Key)**: Never bake API keys into Dockerfiles or hardcode them in services. Load them via environment variables or request headers.

## 2. Coding Standards
- **Style**: Follow PEP 8 for Python. Use lowercase with underscores for functions/variables.
- **Type-Safety**: Use **Pydantic** for all request/response validation. Every API endpoint must have a corresponding schema in `core/schemas.py`.
- **Logging**: Use the structured JSON logger defined in `core/logging_config.py`. Never use `print()`.
- **Error Handling**: Use the global `format_error` helper in `extensions.py` to ensure user-facing errors are human-readable and do not leak stack traces.

## 3. Workflow & AI Orchestration
- **Proprietary Prompting**: LLM prompts must be stored as raw strings in `core/prompts.py` to allow for easy cross-model testing.
- **Structured Output**: Every LLM call MUST specify a JSON schema instruction and use Pydantic to validate the response before returning it to the user.
- **Resilience**: Implement a minimum of 1 retry for LLM empty/malformed responses.

## 4. Documentation
- **AI Notes**: Every major AI-generated module must be documented in `AI_NOTES.md` explaining the "Correction" and "Verification" performed by the developer.
- **Predictability**: Prioritize simple, readable code over "clever" one-liners.
