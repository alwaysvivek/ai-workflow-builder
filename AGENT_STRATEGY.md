# AGENT_STRATEGY.md

This file documents the high-level strategy used to orchestrate AI agents during this project. It moves beyond "simple prompting" to a multi-stage **Agentic Workflow** that ensures the final system is production-grade.

---

## 1. The Planning Phase (AI as Architecture Consultant)

I used AI agents as architectural consultants to explore trade-offs before a single line of code was written.

*   **Conflict Resolution**: When AI suggested a "Production-Heavy" stack (Postgres + Redis + Next.js), I manually overruled it to stick to the core requirements: **Flask + React + SQLite**. 
*   **The Strategy:** I used AI to quickly vet which specific Flask extensions (like `flask-limiter`) were the best fit for this specific scope, allowing me to focus on the "Small Software" philosophy. This ensures the project remains a "Small Software Product" that is easy to audit and run.
*   **Prompt**: *"Given the requirement for a small, understandable system, justify using SQLite over Postgres for this specific project."*
*   **Outcome**: A decision to prioritize **change resilience** and **zero-setup execution**.

---

## 2. The Implementation Phase (AI as Pair-Programmer)

During coding, I used the `.agent/rules.md` file to treat the agent like a junior developer who needs strict guardrails and constant oversight.

*   **Atomic Implementation**: I didn't ask for "The whole project". I asked for atomic components (e.g., "Implement the LLM Service as a clean class with Pydantic validation").
*   **Enforcing Guardrails**: I set a strict **Type-Safe** policy: *"If a Pydantic model can represent this data, you are forbidden from using dicts."* This was enforced via the `.agent/rules.md` file.
*   **Correction**: In several instances, the agent tried to use `json.loads` directly. I manually corrected it to use `model_validate_json` for type safety and checked for common pitfalls like circular imports.

---

## 3. The Verification Phase (AI as Security & QA Auditor)

I treated AI as a "Security & Reliability Auditor" rather than just a code generator.

*   **Edge-Case Hunting**: I prompted the AI specifically to find failures: *"Identify 3 ways this prompt chaining could fail if the LLM returns slightly malformed JSON."*
*   **Reliability Refinement**: Based on that audit, I implemented the **Step Buffer + Cleanup** technique to ensure that even if the LLM adds markdown fences (```json) or conversational noise, the parser remains robust.
*   **Adversarial Testing**: Swapping the AI's role from "Builder" to "Adversary" helped identify the need for the `format_error` utility—ensuring technical jargon never reaches the end-user.

---

## 4. Key Takeaway: The Orchestrator Mindset

I am not a "Consumer" of AI; I am an **Orchestrator**. I use AI to move at high speed on the boilerplate and standard logic (the "Mundane"), so I can focus my energy on the "Critical" elements:
1.  **Schema Reliability** (Validation)
2.  **System Observability** (Structured JSON Logging)
3.  **Error Resilience** (Retries and Human-Readable Messaging)

This project stands as a testament to what is possible when a product-minded engineer guides high-velocity agents toward a specific architectural goal.
