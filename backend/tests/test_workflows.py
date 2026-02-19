import pytest
from app import create_app
from extensions import db
from config import Config
from models import Workflow

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_workflow(client):
    payload = {
        "name": "Test Workflow",
        "steps": [
            {"action": "clean", "params": {}},
            {"action": "summarize", "params": {}}
        ]
    }
    response = client.post('/api/workflows', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Test Workflow"
    assert len(data['steps']) == 2
    assert 'id' in data

def test_create_workflow_invalid(client):
    payload = {
        "name": "Invalid"
        # Missing steps
    }
    response = client.post('/api/workflows', json=payload)
    assert response.status_code == 400

def test_get_workflow(client):
    # Create one first
    payload = {
        "name": "Test Retrieval",
        "description": "Desc",
        "steps": [{"action": "clean"}]
    }
    create_resp = client.post('/api/workflows', json=payload)
    wf_id = create_resp.get_json()['id']
    
    # Get it
    response = client.get(f'/api/workflows/{wf_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Test Retrieval"
    assert data['description'] == "Desc"
