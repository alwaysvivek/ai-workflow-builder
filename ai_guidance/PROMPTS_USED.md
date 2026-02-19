# PROMPTS_USED.md

This file documents the iterative prompting process used effectively to build the **Type-Safe AI Workflow Builder** as part of the **Better Software** technical assessment. It mirrors the development lifecycle from requirements to final polish.

## 1. Project Inception & Structure

**Prompt:**
> "I need to build a 'small software product' using Flask, React, and SQL. The goal is 'Structure' and 'Correctness' over features.
>
> **Idea**: A Workflow Builder for text processing (Clean -> Summarize -> Analyze).
>
> **Constraint**: It must be 'Type-Safe'. The LLM output must be reliable, not just chat.
>
> Propose a file structure that separates 'Core Logic' (Pydantic schemas, Prompts) from 'Web Layout' (Blueprints, React Pages). Avoid circular imports."

**Manual Verification:**
-   **Checked:** Did it use Blueprints? Yes.
-   **Correction:** It initially suggested a complex `apps/` folder structure. I simplified it to `backend/core` and `backend/blueprints` to match the "Small System" requirement.

## 2. Defining The Logic Engine (Pydantic)

**Prompt:**
> "Create a `schemas.py` file using Pydantic. I need models for:
> 1. `WorkflowCreate` (name, steps) - validate that name is not empty.
> 2. `CleanOutput` - has `cleaned_text` string.
> 3. `SummarizeOutput` - has `summary` string.
> 4. `ToneOutput` - has `tone` string and `explanation` string.
>
> Also, writing a generic `LLMStepOutput` that can capture any of these."

**Manual Verification:**
-   **Tested:** I ran a script to `model_validate_json` on dummy data.
-   **Refined:** I added `sanitize_text` validators to the input models to prevent HTML injection at the schema level.

## 3. The Execution Pipeline (Flask + Groq)

**Prompt:**
> "Write a `core/execution.py` module. It should:
> 1. Take a workflow step (ActionType + input).
> 2. formatted prompt = Base Prompt + JSON Schema Instruction.
> 3. Call Groq API (Llama 3).
> 4. Parse the response using the corresponding Pydantic Model.
> 5. Return strict JSON.
>
> Handle the case where the LLM wraps output in markdown code blocks."

**Manual Verification:**
-   **Bug Found:** The LLM sometimes returned `Here is the JSON: ...`.
-   **Fix:** I manually wrote a `parse_step_output` function that strips pre/post text and finds the first `{` and last `}`.

## 4. Frontend Integration (Streaming)

**Prompt:**
> "Create a `useWorkflow` React hook. It needs to:
> 1. POST to `/run_stream`.
> 2. Read NDJSON (Newlines Delimited JSON) parts.
> 3. Update the UI state `currentStep` and `logs` in real-time.
> 4. Handle errors gracefully."

**Manual Verification:**
-   **UX Check:** Verified that the "Loading" spinner appears *per step* and turns into a checkmark when that specific step completes.
-   **Edge Case:** Tested what happens if the network cuts out (added `try/catch` in the stream reader).

## 5. Error Handling Polish

**Prompt:**
> "I'm getting this error: `groq.AuthenticationError: Error code: 401`.
> Use a global error handler to catch this specific exception.
> Return a 401 status code and a clean message: 'Invalid API Key'."

**Manual Verification:**
-   **Verified:** Changed the API Key to `gsk_invalid` and confirmed the UI shows the red error banner with the clean message.

## 6. Architecture Documentation

**Prompt:**
> "Generate a README.md that highlights:
> 1. The 'Type-Safe' nature of the project.
> 2. The explicit choice of Flask over FastAPI (per requirements).
> 3. How to run it with Docker.
>
> Keep the tone professional and engineering-focused."

**Manual Verification:**
-   **Edited:** I manually refined the "Trade-offs" section to be more specific about *why* SQLite was chosen (self-contained artifact).

---

## 7. Iterative Refinement: Dealing with "AI Friction"

Prompting an AI isn't always a "one-shot" success. Here are the key points where I had to iterate to get the standard of engineering required:

*   **Enforcing JSON Mode:** The LLM kept returning "Here is the JSON...". I had to implement a **Refined Anchor** prompt: *"You are a Structured Logic Engine. CRITICAL: You must return the result as a raw JSON string. Do NOT include conversational text."* 
*   **Dealing with API Reliability:** Occasionally, the LLM returned empty strings. I implemented a **Retry Loop** with a specific failure-context prompt: *"The previous attempt failed. Please try again carefully, ensuring you follow the schema exactly."* This dramatically improved workflow pass-rates.
*   **Final Audit Refactor:** I prompted specifically for a redundancy audit: *"Analyze workflows.py and execution.py. Can we consolidate the execution logic?"* Resulting in the `execute_step_with_retry` refactor that merged ~50 lines of duplicate code.

---
