"""
Database Models (Pipeline Stage: Persistence)
===========================================

This module defines the SQLAlchemy ORM models for the application.
It maps Python objects to SQLite database tables.

Schema:
-   `Workflow`: Stores configuration (name, steps).
-   `WorkflowRun`: Tracks execution instances (status, input).
-   `WorkflowStepRun`: Logs individual step results for audit/history.
"""
from extensions import db
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.sqlite import JSON

class Workflow(db.Model):
    __tablename__ = "workflows"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), index=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    steps = db.Column(JSON, nullable=False)  # SQLite supports JSON type via SQLAlchemy dialect
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    runs = db.relationship("WorkflowRun", backref="workflow", lazy=True, cascade="all, delete-orphan")

class WorkflowRun(db.Model):
    __tablename__ = "workflow_runs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey("workflows.id"), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="running") # running, completed, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    step_runs = db.relationship("WorkflowStepRun", backref="workflow_run", lazy=True, cascade="all, delete-orphan")

class WorkflowStepRun(db.Model):
    __tablename__ = "workflow_step_runs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_run_id = db.Column(db.String(36), db.ForeignKey("workflow_runs.id"), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(50), nullable=False)
    output_text = db.Column(db.Text, nullable=True)
