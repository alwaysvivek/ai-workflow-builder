"""
Data Schemas & Validation (Pipeline Stage: Data Integrity)
========================================================

This module defines Pydantic models for request/response validation.
It serves as the contract between Frontend <-> Backend and Backend <-> LLM.

Responsibilities:
-   **Request Validation**: Ensures input payloads (Workflows, Runs) are valid.
-   **Structured Output**: Defines strict schemas for LLM responses (CleanOutput, etc.). to ensure machine-readable results.
"""
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from core.prompts import ActionType
from core.sanitizer import sanitize_text, sanitize_name

class WorkflowStep(BaseModel):
    action: ActionType
    params: Optional[dict] = Field(default_factory=dict)

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]

class WorkflowCreate(WorkflowBase):
    @field_validator('name')
    @classmethod
    def sanitize_workflow_name(cls, v: str) -> str:
        v = sanitize_name(v)
        if not v:
            raise ValueError("Workflow name cannot be empty")
        return v

    @field_validator('description')
    @classmethod
    def sanitize_workflow_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = sanitize_text(v, max_length=1000)
        return v

    @field_validator('steps')
    @classmethod
    def check_consecutive_duplicates(cls, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        if not steps:
            return steps
            
        for i in range(len(steps) - 1):
            if steps[i].action == steps[i+1].action:
                raise ValueError(f"Consecutive duplicate actions are not allowed: Step {i+1} and Step {i+2} are both '{steps[i].action.value}'")
        return steps

class WorkflowRead(WorkflowBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowRunCreate(BaseModel):
    input_text: str

    @field_validator('input_text')
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = sanitize_text(v)
        if not v:
            raise ValueError("Input text cannot be empty")
        return v

class WorkflowStepRunRead(BaseModel):
    id: UUID
    workflow_run_id: UUID
    step_order: int
    step_type: str
    output_text: str
    model_config = ConfigDict(from_attributes=True)

class WorkflowRunRead(BaseModel):
    id: UUID
    workflow_id: UUID
    input_text: str
    status: str
    created_at: datetime
    step_runs: List[WorkflowStepRunRead] = []
    model_config = ConfigDict(from_attributes=True)

class KeyValidationRequest(BaseModel):
    api_key: str

    @field_validator('api_key')
    @classmethod
    def validate_api_key_format(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("API key cannot be empty")
        if len(v) > 256:
            raise ValueError("API key exceeds maximum length")
        return v

# --- Structured Output Validation for LLM Responses ---

class LLMStepOutput(BaseModel):
    """
    Validates and structures the output from each LLM step.
    Used to ensure the LLM response is well-formed before
    passing it to the next step in the chain.
    """
    content: str
    step_order: int
    action: str
    is_valid: bool = True

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("LLM returned empty output")
        return v

# --- Specific Action Models (Strict Structured Output) ---

class CleanOutput(BaseModel):
    cleaned_text: str = Field(..., description="The cleaned and corrected text.")

class SummarizeOutput(BaseModel):
    summary: str = Field(..., description="A concise summary of the input text.")

class KeyPointsOutput(BaseModel):
    points: List[str] = Field(..., description="A list of key points extracted from the text.")

class SimplifyOutput(BaseModel):
    simplified_text: str = Field(..., description="The simplified version of the input text.")

class AnalogyOutput(BaseModel):
    analogy: str = Field(..., description="An analogy or example explaining the concept.")

class ClassifyOutput(BaseModel):
    category: str = Field(..., description="The category the text belongs to.")

class ToneOutput(BaseModel):
    tone: str = Field(..., description="The emotional tone of the text.")
    explanation: str = Field(..., description="Brief explanation of why this tone was selected.")

class GenericOutput(BaseModel):
    result: str = Field(..., description="The result of the operation.")
