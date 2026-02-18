import os
from pathlib import Path
from dotenv import load_dotenv

# Calculate path to .env file (parent of backend is root)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    PROJECT_NAME = "Workflow Builder"
    VERSION = "2.0.0"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    
    # Database (SQLite)
    # Using a file-based SQLite database located in the backend directory
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///workflow_builder.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

config = Config()
