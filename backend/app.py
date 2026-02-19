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
import os
from flask import send_from_directory

def create_app(config_class=config):
    # Initialize structured logging first
    setup_logging()
    
    # Setup static folder path
    # In Docker, we copy dist to /app/static. Locally, we look at ../frontend/dist
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
         static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

    app = Flask(__name__, static_folder=static_dir, static_url_path='/')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    CORS(app) # Broad CORS for the API layer

    # Register blueprints with /api prefix
    app.register_blueprint(system_bp, url_prefix='/api')
    app.register_blueprint(workflows_bp, url_prefix='/api')
    
    # Create DB tables within app context
    with app.app_context():
        db.create_all()

    # Serve React App
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # 1. DO NOT handle anything that looks like an API call (starts with api/)
        # This allows Blueprints to handle those routes properly.
        if path.startswith('api/'):
            return {"error": "API route not found"}, 404

        # 2. If the path exists in the static folder, serve it
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # 3. Otherwise, serve index.html for React Router to handle
        # This covers our home page and status page
        return send_from_directory(app.static_folder, 'index.html')
        
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "API route not found"}), 404
        return send_from_directory(app.static_folder, 'index.html')
        
    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal Server Error"}, 500
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5001)
