import pytest
from app import create_app
from extensions import db, limiter
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'

def test_validate_key_missing(client):
    response = client.post('/api/validate-key', json={})
    assert response.status_code == 400

def test_validate_key_empty(client):
    response = client.post('/api/validate-key', json={'api_key': '   '})
    assert response.status_code == 400

def test_get_runs_empty(client):
    # Ensure DB is clean
    with client.application.app_context():
        db.create_all()
        
    response = client.get('/api/runs')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0
