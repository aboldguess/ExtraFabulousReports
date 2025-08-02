import os
import sys

# Ensure the application module is discoverable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db

@pytest.fixture
def client():
    """Provide a test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_register_and_login(client):
    """Register a user then log in and access document list."""
    # Register new user
    client.post('/register', data={'username': 'alice', 'password': 'pw'})
    # Login
    response = client.post('/login', data={'username': 'alice', 'password': 'pw'}, follow_redirects=True)
    assert b'Your Documents' in response.data
