# .agent/rules.md

This file defines the strict architectural and coding standards that were used to guide AI agents during the development of this project. It ensures that generated code remains simple, correct, and maintains clear boundaries.

---

## 1. Architectural Constraints

*   **No FastAPI**: Despite AI's preference for FastAPI, this project **MUST** use Flask (API) and vanilla Python as per the core architectural guidelines.
*   **Blueprint Pattern**: All routes must be organized into `blueprints/`. No route logic in `app.py`.
*   **Extensions Isolation**: Initializations (DB, Limiter) must happen in `extensions.py` to prevent circular imports.
*   **Business Logic Location**: All LLM logic, sanitization, and data parsing must live in `core/`. Blueprints only handle HTTP request/response.

---

## 2. Coding Standards

*   **Strict Type-Safety**: 
    *   Every user-facing input and LLM-facing output **MUST** use a Pydantic model. 
    *   Direct dictionary access (`data['key']`) is forbidden if a schema exists.
*   **Simplicity > Cleverness**: 
    *   Avoid complex abstractions or "one-liners". 
    *   Use explicit `try-except` blocks with logging instead of generic catching.
*   **Vanilla CSS**: Avoid heavy UI libraries. Use Tailwind utility classes directly in React components.

---

## 3. Security & Validation Rules

*   **Zero-Trust Input**: All text inputs must be run through `sanitize_text` via Pydantic `@field_validator`.
*   **No API Key Persistence**: Never store API keys in the database. Always use `x-groq-api-key` headers for execution.
*   **Human-Readable Errors**: AI must never return raw exception strings. Use the `format_error` utility to return clean, actionable messages.

---

## 4. LLM Interaction Rules

*   **JSON Mode Only**: All LLM prompts must include a `CRITICAL OUTPUT INSTRUCTION` that references a specific Pydantic JSON schema.
*   **No Conversational Filler**: Direct the LLM to return *only* the raw JSON string.
*   **Retry Logic**: Implement a single-retry "Repair" path for any step that returns empty or invalid output.
