"""
Workflows Blueprint (Pipeline Stage: Routing & Control)
=======================================================

This module defines the API routes for managing and executing workflows.
It acts as the controller layer in the MVC architecture.

Responsibilities:
-   **Create**: attributes, validation.
-   **Retrieve**: Fetch workflow details.
-   **Execute (Stream/Sync)**: Orcestrates the execution by calling `core.execution` helpers.
    -   Handles API Key extraction from headers.
    -   Manages database transactions for Runs and Steps.
    -   Streams responses (NDJSON) or returns JSON payloads.
"""
from flask import Blueprint, jsonify, request, Response, stream_with_context
from extensions import db, limiter
from models import Workflow, WorkflowRun
from core.llm import llm_service
from core.prompts import PROMPTS
from core.logging_config import get_logger
import json
import uuid
import groq
from core.schemas import WorkflowCreate
from extensions import format_error
from pydantic import ValidationError

workflows_bp = Blueprint('workflows', __name__)
logger = get_logger(__name__)

@workflows_bp.route('/workflows', methods=['POST'])
def create_workflow():
    data = request.get_json()
    if not data:
         return jsonify({"error": "Missing input data"}), 400
         
    try:
        # Validate using Pydantic Schema
        validated_data = WorkflowCreate(**data)
        
        # Create SQLAlchemy model from validated data
        new_workflow = Workflow(
            name=validated_data.name,
            description=validated_data.description,
            steps=[s.model_dump() for s in validated_data.steps]
        )
        db.session.add(new_workflow)
        db.session.commit()
        
        logger.info(f"Workflow created: {new_workflow.id}")
        return jsonify({
            "id": new_workflow.id,
            "name": new_workflow.name,
            "steps": new_workflow.steps
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return jsonify({"error": format_error(e)}), 400
        
    except Exception as e:
        logger.error("Failed to create workflow", exc_info=True)
        return jsonify({"error": format_error(e)}), 500

@workflows_bp.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    workflow = db.session.get(Workflow, workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    
    return jsonify({
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "steps": workflow.steps
    }), 200

@workflows_bp.route('/workflows/<workflow_id>/run_stream', methods=['POST'])
@limiter.limit("5/minute")
def run_workflow_stream(workflow_id):
    workflow = db.session.get(Workflow, workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    data = request.get_json()
    input_text = data.get('input_text') if data else None
    
    if not input_text:
         return jsonify({"error": "Missing input_text"}), 400
         
    # Generate run ID upfront
    run_id = str(uuid.uuid4())
    
    # Create Run Record (Commit immediately so it exists)
    new_run = WorkflowRun(
        id=run_id,
        workflow_id=workflow.id,
        input_text=input_text,
        status="running"
    )
    db.session.add(new_run)
    db.session.commit()
    
    # Pre-load steps to avoid DetachedInstanceError inside generator
    # The workflow object might be detached when the generator runs later
    workflow_steps = workflow.steps
    
    api_key = request.headers.get("x-groq-api-key")
    client = llm_service.get_client(api_key)

    def generate():
        current_input = input_text
        
        if not client:
            logger.warning(f"API key missing for run {run_id}")
            yield json.dumps({"error": "API Key missing"}) + "\n"
            # Update status to failed
            with db.session.begin(): # Use new transaction
                 run_to_update = db.session.get(WorkflowRun, run_id)
                 if run_to_update:
                     run_to_update.status = "failed"
            return

        try:
             from core.execution import get_step_prompt, save_step_run, parse_step_output

             for index, step in enumerate(workflow_steps):
                action = step.get('action')
                yield json.dumps({"step": index + 1, "action": action, "status": "started"}) + "\n"
                
                # 1. Get Prompt
                try:
                    prompt = get_step_prompt(action, current_input)
                except ValueError as e:
                    logger.error(str(e))
                    yield json.dumps({"error": str(e)}) + "\n"
                    return

                # 2. Execution with Retry
                logger.info(f"Executing action {action} for run {run_id}")
                from core.execution import execute_step_with_retry
                
                step_output, attempts = execute_step_with_retry(client, action, current_input)
                
                # Emit chunk for entire content since we are using sync call for reliability
                # This matched the user's preference for 'everything done at once' feel
                if step_output:
                    yield json.dumps({"step": index + 1, "chunk": step_output}) + "\n"
                
                # 3. Save Step
                save_step_run(run_id, index + 1, action, step_output)
                
                # Update current input for next step
                current_input = step_output
                yield json.dumps({"step": index + 1, "status": "completed", "final_output": step_output}) + "\n"

             # Mark run as completed
             run_to_complete = db.session.get(WorkflowRun, run_id)
             run_to_complete.status = "completed"
             db.session.commit()
             logger.info(f"Run {run_id} completed successfully")
             yield json.dumps({"status": "workflow_completed", "run_id": run_id}) + "\n"
             
        except groq.AuthenticationError:
            logger.error(f"Invalid API Key for run {run_id}")
            # Update status to failed
            try:
                 with db.session.begin():
                    run_to_fail = db.session.get(WorkflowRun, run_id)
                    if run_to_fail:
                         run_to_fail.status = "failed"
            except:
                pass
            yield json.dumps({"error": "Invalid API Key. Please check your credentials."}) + "\n"
            return

        except Exception as e:
            logger.error(f"Run {run_id} failed", exc_info=True)
            # Try to update status
            try:
                 run_to_fail = db.session.get(WorkflowRun, run_id)
                 run_to_fail.status = "failed"
                 db.session.commit()
            except:
                pass 
            yield json.dumps({"error": format_error(e)}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

@workflows_bp.route('/workflows/<workflow_id>/run', methods=['POST'])
@limiter.limit("5/minute")
def run_workflow_sync(workflow_id):
    """
    Synchronous execution of workflow.
    Blocks until completion and returns full result.
    More robust than streaming for simpler clients/networks.
    """
    workflow = db.session.get(Workflow, workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404

    data = request.get_json()
    input_text = data.get('input_text') if data else None
    
    if not input_text:
         return jsonify({"error": "Missing input_text"}), 400
         
    # Generate run ID upfront
    run_id = str(uuid.uuid4())
    
    # Create Run Record
    new_run = WorkflowRun(
        id=run_id,
        workflow_id=workflow.id,
        input_text=input_text,
        status="running"
    )
    db.session.add(new_run)
    db.session.commit()
    
    # Pre-load steps to avoid DetachedInstanceError
    workflow_steps = workflow.steps
    
    api_key = request.headers.get("x-groq-api-key")
    client = llm_service.get_client(api_key)
    
    if not client:
        return jsonify({"error": "API Key missing"}), 400

    step_results = []
    current_input = input_text
    
    try:
        from core.execution import get_step_prompt, save_step_run, parse_step_output

        for index, step in enumerate(workflow_steps):
            action = step.get('action')
            
            # 1. Get Prompt
            try:
                prompt = get_step_prompt(action, current_input)
            except ValueError as e:
                logger.error(str(e))
                return jsonify({"error": str(e)}), 400

            # 2. Execution with Retry
            from core.execution import execute_step_with_retry
            step_output, attempts = execute_step_with_retry(client, action, current_input)
            
            # 3. Save Step
            save_step_run(run_id, index + 1, action, step_output)
            
            step_results.append({
                "step": index + 1,
                "action": action,
                "status": "completed",
                "final_output": step_output
            })
            
            # Update current input for next step
            current_input = step_output

        # Mark run as completed
        run_to_complete = db.session.get(WorkflowRun, run_id)
        run_to_complete.status = "completed"
        db.session.commit()
        
        return jsonify({
            "status": "workflow_completed",
            "run_id": run_id,
            "steps": step_results
        }), 200
         
    except groq.AuthenticationError:
        logger.error(f"Invalid API Key for run {run_id}")
        # Update status to failed
        try:
             run_to_fail = db.session.get(WorkflowRun, run_id)
             run_to_fail.status = "failed"
             db.session.commit()
        except:
             pass
        return jsonify({"error": "Invalid API Key. Please check your credentials."}), 401

    except Exception as e:
        logger.error(f"Run {run_id} failed", exc_info=True)
        # Try to update status
        try:
                run_to_fail = db.session.get(WorkflowRun, run_id)
                run_to_fail.status = "failed"
                db.session.commit()
        except:
            pass 
        return jsonify({"error": format_error(e)}), 500
