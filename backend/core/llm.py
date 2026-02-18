"""
LLM Service Layer (Pipeline Stage: External Integration)
======================================================

This module manages the connection to the Groq API.
It handles client initialization and abstraction.

Responsibilities:
-   **Client Management**: Singleton or per-request client creation.
-   **Configuration**: Loads API keys from environment or request headers.
"""
from groq import Groq
from config import config

class LLMService:
    def __init__(self):
        self.default_client = None
        if config.GROQ_API_KEY:
            self.default_client = Groq(api_key=config.GROQ_API_KEY)

    def get_client(self, api_key: str = None):
        if api_key:
            return Groq(api_key=api_key)
        return self.default_client

llm_service = LLMService()
