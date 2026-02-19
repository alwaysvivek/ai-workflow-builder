# AI_NOTES.md

AI tools were used selectively during the **planning, implementation, and refinement phases** of this project to accelerate development while ensuring architectural integrity.
All final architectural decisions, Pydantic schemas, and error handling logic were reviewed and finalized manually.

To show how I managed these tools, I have included **AI Guidance Files**:
*   [**.agent/rules.md**](file:///.agent/rules.md): Defines the strict coding standards and architectural boundaries enforced on the AI.
*   [**AGENT_STRATEGY.md**](file:///AGENT_STRATEGY.md): Documents the high-level orchestration mindset used to transition from "Drafting" to "Reliable Engineering".
*   [**PROMPTS_USED.md**](file:///PROMPTS_USED.md): A detailed log of critical prompts and their manual validation.


---

## 1. Requirement Analysis: "Simple > Complex"
**Prompting Context:** 
I used AI to evaluate potential project ideas and suggest structures. 
- **The Friction:** AI initially pushed for heavy stacks (FastAPI, PostgreSQL, Dockerized Redis). 
- **My Override:** I explicitly steered the project back to **Flask + SQLite** for this **Better Software** submission to ensure it remains a "Small Software Product" that is easy to audit and run without heavy infrastructure overhead.

**What I Verified:**
*   Confirmed that the "Workflow Builder" concept allowed for demonstrating **Interface Safety** (via Pydantic schemas) over simple CRUD.
*   Decided against complex UI libraries (Shadcn/MUI) in favor of **Tailwind functionality** to demonstrate "Simple > Clever".
*   Verified that the "Workflow Builder" concept allowed for demonstrating **Interface Safety** (via Pydantic schemas) and **Observability** (via step logs).

**Tool Used:**
Antigravity (Google)

---

## 2. Architecture & Tech Stack Decisions

**Prompt Used:**
> "Design a folder structure for a Flask + React application that avoids circular imports and separates 'Business Logic' from 'HTTP Routes'. I want to use Blueprints and an Application Factory pattern."

**Purpose:**
To establish a scalable, professional codebase structure from Day 1.

**Why AI Was Used:**
To generate the boilerplate for the `create_app` factory pattern and Flask Blueprints, which can be tedious to type out manually.

**What I Came Up With Myself:**
*   **Core vs. Blueprints Separation**: I enforced the `backend/core/` directory for pure logic (Prompts, LLM Service, Schemas) vs `backend/blueprints/` for routes.
*   **Extensions Isolation**: I manually created `extensions.py` to house the Singleton instances of the Database and Rate Limiter. This is a common pitfall when using agents—they often put these in `app.py`, leading to circular imports.
*   **Groq Selection**: I chose Groq over OpenAI/Gemini specifically for its speed/cost ratio for this high-volume text processing task.

**Tool Used:**
Antigravity (Google)

---

## 3. Type-Safety & Validation (The "Differentiator")

**Prompt Used:**
> "I want to make this LLM application deterministic. Create Pydantic models for 7 specific text processing actions (Clean, Summarize, etc.) and write a prompt strategy that forces the LLM to output valid JSON matching these schemas."

**Purpose:**
To implement the "Type-Safe" aspect of the project, turning vague natural language into reliable API contracts.

**Why AI Was Used:**
To draft the initial Pydantic models (`CleanOutput`, `SummarizeOutput`) and the JSON-enforcing system prompts.

**Manual Validation Performed:**
*   **Schema Enforcement**: I manually verified that the backend *actually* parses the output using `model_validate_json` and raises errors if the LLM hallucinates keys.
*   **Fallback Logic**: Wrote the `parse_step_output` function to handle markdown code fences (```json) which LLMs often include despite instructions.
*   **Sanitization**: Added `sanitize_text` validators to the Pydantic input models to prevent XSS and injection attacks.

**Tool Used:**
Antigravity (Google)

---

## 4. Error Handling & "Human Readability"

**Prompt Used:**
> "The error 'Error code: 401 - {'error': ...}' is ugly. Write a global error formatter in Python that strips technical jargon and Pydantic JSON dumps, converting them into single human-readable sentences."

**Purpose:**
To improve the User Experience (UX) and "Simplicity" score.

**Why AI Was Used:**
To write the regex and string parsing logic in `extensions.py` that cleans up complex exception strings.

**What I Verified Myself:**
*   Tested with an **Invalid API Key** to ensure it says "Invalid API Key" and not a stack trace.
*   Tested with **Empty Input** to ensure it says "Input cannot be empty".
*   Confirmed that `groq.AuthenticationError` is caught explicitly in `workflows.py`.

---

## 5. Coding Assistance

**Tools Used:**
-   **Antigravity (Google)**: Primary coding agent. Used for writing code, running terminal commands, refactoring file structures, and fixing bugs.
-   **Claude 3.5 Sonnet / GPT-4o**: Used via the agent for high-level reasoning and debugging tricky React `useEffect` loops.

**Why Different Tools:**
*   **Antigravity** has file-system access, making it effectively a "Pair Programmer" that can run tests and fix lints.
*   **LLMs** were used for generating the "Content" (Prompts, Seeds) and "Strategy" (Architecture decisions).

---

## 6. Post-Audit: Production Hardening

**Prompt Used:**
> "Audit this `workflows.py` file. Point out any security risks, unhandled edge cases, or lack of observability."

**What I Did:**
*   **Rate Limiting**: Added `Flask-Limiter` to protect the LLM endpoints (5 req/min).
*   **CORS**: Restricted CORS to localhost for development.
*   **Logging**: Replaced `print()` statements with a structured JSON logger in `core/logging_config.py`.
*   **Atomic Step Validation**: Implemented a strategy where each workflow step is validated via Pydantic *before* being emitted to the NDJSON stream. This prevents the UI from receiving or rendering malformed partial JSON and ensures data integrity across the pipeline.

---

## 7. UX Refinement: Synchronous "Batch" Experience

**Prompt:**
> "Users are confused when the spinner sits on 'Step 1' during the entire synchronous execution. Modify the UI to show a global 'Processing Workflow' state instead of a per-step spinner."

**Purpose:**
To better manage user expectations for the synchronous execution model.

**Why AI Was Used:**
To quickly refactor the React component conditional logic to swap the step-based loader for a top-level banner.

**What I Verified Myself:**
*   **Design Choice**: I deliberately chose **Synchronous Execution** over Streaming for the final submission. While streaming is "flashier", valid JSON parsing of partial streams is fragile. Sync execution allows for atomic database transactions and perfect Pydantic validation of the *entire* chain before showing it to the user.
*   **Visual Feedback**: Changed the UI to show a "Global Loader" so users understand the whole batch is processing, rather than thinking it's stuck on Step 1.

---

## 8. Final Engineering Reflection: The Orchestrator Mindset

This project wasn't just a "one-shot" generation. It was an iterative process of using AI to handle the boilerplate while I enforced the architectural guardrails.

*   **Logic Consolidation:** During a final audit, I noticed the "Retry on failure" logic was duplicated in both Sync and Stream endpoints. I orchestrated a refactor to extract this into `execute_step_with_retry` in `core/execution.py`, deleting ~50 lines of redundant code.
*   **Iterative Friction:** I treated AI as a **Junior Developer with Infinite Speed**. I gave it the "Rules" (standards), and I acted as the "Senior Reviewer." Every "Aha!" moment—from handling markdown fences to global error formatting—was the result of me pushing the AI to do better engineering.

---

## 9. Reliability Checks Applied to AI-Assisted Code

I followed this checklist for every module:

1.  **Static Analysis**: Every file was checked for PEP 8 compliance and logic errors.
2.  **Circular Dependency Check**: Verified that the AI didn't introduce implicit imports between `core/` and `blueprints/`.
3.  **Boundary Leakage**: Ensured that the LLM Service (`services/llm.py`) does not contain any HTTP/Flask logic, and Blueprints do not contain any Prompt-Engineering logic.
4.  **Schema Validity**: Manually triggered validation failures (e.g., sending invalid JSON to the backend) to confirm that Pydantic properly catches and formats the error.
5.  **Adversarial Prompts**: Tested the "Action" steps with gibberish input to verify that the system returns a safe "Failure to Parse" state rather than crashing.

---

## 10. Guidance File Navigation

For a deep dive into the constraints and logs used during development, please refer to the following files (all located in `ai_guidance/`):

- [**rules.md**](./rules.md): Architectural guardrails.
- [**AGENT_STRATEGY.md**](./AGENT_STRATEGY.md): High-level orchestration.
- [**PROMPTS_USED.md**](./PROMPTS_USED.md): Iterative prompt logs.
