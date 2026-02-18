from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import ValidationError

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

def format_error(e: Exception) -> str:
    """
    Converts various exception types into a single human-readable string.
    Removes technical jargon and JSON dumps.
    """
    if isinstance(e, ValidationError):
        # Extract the first error message and location to make it friendly
        # e.g., "Invalid input for 'name': Field required"
        errors = e.errors()
        if errors:
            first_err = errors[0]
            loc = " -> ".join(str(l) for l in first_err.get('loc', []))
            msg = first_err.get('msg', 'Invalid input')
            # Clean up Pydantic's default messages if needed
            msg = msg.replace("Value error, ", "")
            if loc:
                return f"{msg} (Field: {loc})"
            return msg
        return "Invalid input data"
    
    # Handle other specific types if needed
    
    
    msg = str(e)
    
    # Handle Groq/API Error strings that contain JSON
    # Example: "Error code: 401 - {'error': {'message': 'Invalid API Key', ...}}"
    if "Error code:" in msg and "{" in msg:
        try:
            import json
            import re
            
            # Extract JSON part
            json_part = msg.split("-", 1)[1].strip()
            # The string might use single quotes, valid JSON needs double.
            # Simple heuristic: if it looks like a dict, try to parse
            if json_part.startswith("{"):
                # converting simple python dict string to json if possible
                # This is hacky but effective for standard library stringifications
                json_part = json_part.replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
                error_dict = json.loads(json_part)
                
                # Check for standard OAuth/API error structures
                if 'error' in error_dict:
                    inner = error_dict['error']
                    if isinstance(inner, dict) and 'message' in inner:
                        return inner['message']
                    if isinstance(inner, str):
                        return inner
        except:
            # Fallback to simple string cleaning if parsing fails
            pass
            
    # Generic cleanup
    if "400 Bad Request:" in msg:
        msg = msg.replace("400 Bad Request:", "").strip()
    if "Error code: 401" in msg or "Invalid API Key" in msg:
        return "Invalid API Key. Please check your credentials."
        
    return msg
