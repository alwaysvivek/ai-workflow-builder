"""
Application Entry Point & Pipeline Overview
===========================================

This file initializes the Flask application and orchestrates the entire request processing pipeline.

Pipeline Flow:
1.  **Request Arrival**: Requests hit the Flask app.
2.  **Middleware**:
    -   `CORS`: Handles cross-origin requests from the React frontend.
    -   `Limiter`: Applies rate limits (e.g., 5 requests/minute for LLM endpoints) to prevent abuse.
3.  **Routing (Blueprints)**:
    -   `system_bp`: Handles health checks, API key validation, and retrieving run history.
    -   `workflows_bp`: Handles workflow creation, retrieval, and execution (Sync & Stream).
4.  **Core Execution**:
    -   Routes delegate to `core.execution` which manages prompt assembly, LLM interaction, and step persistence.
5.  **Response**: JSON responses (or NDJSON streams) are returned to the client.

Key Components:
-   `extensions.py`: Singleton instances of DB and Limiter.
-   `config.py`: Environment-based configuration.
"""
from flask import Flask
from flask_cors import CORS
from extensions import db, limiter
from config import config
from blueprints.system import system_bp
from blueprints.workflows import workflows_bp
from core.logging_config import setup_logging

def create_app(config_class=config):
    # Initialize structured logging first
    setup_logging()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}}) # Configure more strictly for prod if needed
    
    # Register blueprints
    app.register_blueprint(system_bp)
    app.register_blueprint(workflows_bp)
    
    # Create DB tables within app context
    with app.app_context():
        db.create_all()
        
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not Found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal Server Error"}, 500
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5001)
