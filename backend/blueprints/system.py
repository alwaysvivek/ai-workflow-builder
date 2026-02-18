"""
System Blueprint (Pipeline Stage: Support & Maintenance)
======================================================
This module handles system-level operations and metadata retrieval.

Responsibilities:
-   **Health Checks**: Verifies database connectivity.
-   **Validation**: Confirms API Key validity with external provider (Groq).
-   **Run History**: Fetches past execution logs for audit and review.
"""
from flask import Blueprint, jsonify, request
from extensions import db, limiter
from models import WorkflowRun
from groq import Groq
from core.logging_config import get_logger

system_bp = Blueprint('system', __name__)
logger = get_logger(__name__)

@system_bp.route('/health', methods=['GET'])
@limiter.limit("30/minute")
def health_check():
    try:
        # Check specific table existence to verify DB is actually usable
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        return jsonify({"status": "unhealthy", "error": "Service unavailable"}), 500

@system_bp.route('/validate-key', methods=['POST'])
@limiter.limit("10/minute")
def validate_key():
    data = request.get_json()
    if not data or 'api_key' not in data:
        return jsonify({"valid": False, "error": "API key missing"}), 400
    
    api_key = data['api_key']
    
    try:
        # Validate format locally first
        if not api_key.strip():
             return jsonify({"valid": False, "error": "API key empty"}), 400
             
        # Actual validation against Groq
        test_client = Groq(api_key=api_key)
        test_client.models.list()
        logger.info("API key validated successfully")
        return jsonify({"valid": True}), 200
    except Exception as e:
        logger.warning(f"API key validation failed: {str(e)}")
        return jsonify({"valid": False, "error": "Invalid API Key or connection failed"}), 401

@system_bp.route('/runs', methods=['GET'])
@limiter.limit("60/minute")
def get_runs():
    try:
        # Simple pagination
        limit = request.args.get('limit', 5, type=int)
        runs = WorkflowRun.query.order_by(WorkflowRun.created_at.desc()).limit(limit).all()
        
        results = []
        for run in runs:
            # Manually serialize since we don't have Pydanticorm_mode here yet
            results.append({
                "id": run.id,
                "workflow_id": run.workflow_id,
                "input_text": run.input_text,
                "status": run.status,
                "created_at": run.created_at.isoformat(),
                "status": run.status,
                "created_at": run.created_at.isoformat(),
                # Include steps for details view
                "step_runs": [{
                    "step": s.step_order,
                    "action": s.step_type,
                    "output": s.output_text
                } for s in run.step_runs]
            })
            
        return jsonify(results), 200
    except Exception as e:
        logger.error("Failed to fetch runs", exc_info=True)
        return jsonify({"error": "Failed to fetch run history"}), 500
