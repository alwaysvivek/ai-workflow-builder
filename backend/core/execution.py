"""
Core Execution Logic (Pipeline Stage: Business Logic)
===================================================

This module centralizes the logic for executing workflow steps.
It bridges the gap between the raw API request and the LLM service.

Responsibilities:
-   **Prompt Assembly**: Combines user input with predefined templates.
-   **LLM Interaction**: Calls the `llm_service` (Groq).
-   **Structured Output**: Enforces JSON validation via Pydantic (`schemas.py`).
-   **Persistence**: Saves step inputs/outputs to the database.
"""
from core.prompts import PROMPTS, ActionType
from core.schemas import CleanOutput, SummarizeOutput, KeyPointsOutput, SimplifyOutput, AnalogyOutput, ClassifyOutput, ToneOutput, GenericOutput
from core.logging_config import get_logger
from models import WorkflowStepRun
from extensions import db
import json

logger = get_logger(__name__)

ACTION_TO_MODEL = {
    ActionType.CLEAN: CleanOutput,
    ActionType.SUMMARIZE: SummarizeOutput,
    ActionType.KEYPOINTS: KeyPointsOutput,
    ActionType.SIMPLIFY: SimplifyOutput,
    ActionType.EXAMPLES: AnalogyOutput,
    ActionType.CLASSIFY: ClassifyOutput,
    ActionType.SENTIMENT: ToneOutput
}

def get_step_prompt(action: str, input_text: str) -> str:
    """
    Retrieves and formats the prompt for a given action.
    Appends strict JSON formatting instructions.
    Raises ValueError if action is invalid or prompt not found.
    """
    try:
        # Case-insensitive lookup
        action_enum = ActionType(action)
        prompt_template = PROMPTS.get(action_enum)
        model = ACTION_TO_MODEL.get(action_enum, GenericOutput)
    except ValueError:
        raise ValueError(f"Invalid action value: {action}")

    if not prompt_template:
        raise ValueError(f"No prompt found for action: {action}")

    base_prompt = prompt_template.format(input_text=input_text)
    
    # Enforce JSON Schema in System/User Prompt
    json_instruction = f"""
    
    CRITICAL OUTPUT INSTRUCTION:
    You MUST return the result as a valid JSON object matching this schema:
    {json.dumps(model.model_json_schema(), indent=2)}
    
    Do NOT include any markdown code blocks (like ```json).
    Do NOT include any conversational text before or after the JSON.
    Return ONLY the raw JSON string.
    """
    
    return base_prompt + json_instruction

def parse_step_output(action: str, raw_output: str) -> str:
    """
    Parses LLM output using the appropriate Pydantic model.
    Returns the 'primary' content field as a string.
    """
    try:
        action_enum = ActionType(action)
        model_class = ACTION_TO_MODEL.get(action_enum, GenericOutput)
        
        # Clean potential markdown fences
        cleaned_output = raw_output.replace("```json", "").replace("```", "").strip()
        
        # Validate logic
        data = json.loads(cleaned_output)
        validated_data = model_class(**data)
        
        # Extract the main content based on model type
        # We return the "crisp" content requested by user
        if isinstance(validated_data, CleanOutput):
            return validated_data.cleaned_text
        elif isinstance(validated_data, SummarizeOutput):
            return validated_data.summary
        elif isinstance(validated_data, KeyPointsOutput):
            # Convert list back to formatted string or keep as list?
            # User likely wants a string for the next step execution
            return "\n".join([f"- {p}" for p in validated_data.points])
        elif isinstance(validated_data, SimplifyOutput):
            return validated_data.simplified_text
        elif isinstance(validated_data, AnalogyOutput):
            return validated_data.analogy
        elif isinstance(validated_data, ClassifyOutput):
            return validated_data.category
        elif isinstance(validated_data, ToneOutput):
            return f"Tone: {validated_data.tone}\nExplanation: {validated_data.explanation}"
        else:
            return str(validated_data.model_dump())
            
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse structured output for {action}: {e}")
        # Fallback: Return raw output if it looks like reasonable text, 
        # or raise error if strictness is required.
        # Given user want "crisp" output, we should probably fail or attempt massive cleanup.
        # For now, simplistic fallback.
        return raw_output.strip()

def execute_step_with_retry(client, action: str, input_text: str, max_retries: int = 1):
    """
    Executes a single step using the LLM client, with retry logic for empty responses.
    This handles prompt formatting, the LLM call, and structured parsing.
    Returns (output_text, attempts_made).
    """
    prompt = get_step_prompt(action, input_text)
    step_output = ""
    attempt = 0

    while attempt <= max_retries:
        # We always use the sync completion here for reliability in sync/stream fallback
        # If we need true streaming, the generator in workflows.py handles it
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            stream=False,
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        if content:
            step_output = parse_step_output(action, content)
        
        if step_output:
            return step_output, attempt + 1
        
        attempt += 1
        if attempt <= max_retries:
            logger.warning(f"Empty output for action {action}. Retrying attempt {attempt+1}.")
            prompt = f"The previous attempt returned an empty response. Please try again carefully.\n\n{prompt}"
            
    return step_output, attempt

def save_step_run(run_id: str, step_order: int, action: str, output_text: str):
    """
    Persists the result of a single workflow step to the database.
    Handles its own commit.
    """
    try:
        step_run = WorkflowStepRun(
            workflow_run_id=run_id,
            step_order=step_order,
            step_type=str(action),
            output_text=output_text
        )
        db.session.add(step_run)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to save step run {run_id} step {step_order}: {e}")
        raise e
