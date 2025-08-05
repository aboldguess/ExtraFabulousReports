import os
import sys

# Ensure the application module is discoverable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from xfabreps_app import app, db, Document, render_figures_and_refs, build_equation

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


def test_instructions_and_help_pages(client):
    """Ensure the informational pages render without authentication."""
    assert b'Instructions' in client.get('/instructions').data
    assert b'Help' in client.get('/help').data


def test_navbar_links_visible_after_login(client):
    """After logging in, the navigation bar should expose instruction and help links."""
    client.post('/register', data={'username': 'bob', 'password': 'pw'})
    response = client.post('/login', data={'username': 'bob', 'password': 'pw'}, follow_redirects=True)
    # The document list page should include the navigation links
    assert b'Instructions' in response.data
    assert b'Help' in response.data


def test_render_figures_and_refs():
    """Custom figure and reference syntax expands to LaTeX code."""
    sample = (
        "See {{ref:sample}} for details.\n"
        "{{figure:static/uploads/img.png|Example caption|sample}}"
    )
    processed = render_figures_and_refs(sample)
    assert "\\includegraphics{static/uploads/img.png}" in processed
    assert "\\caption{Example caption}" in processed
    assert "Figure \\ref{fig:sample}" in processed


def test_build_equation():
    """Equation builder should assemble a full LaTeX equation block."""
    result = build_equation("E", "mc^2", label="mass_energy")
    # The environment lines should wrap the expression
    assert "\\begin{equation}" in result
    assert "E = mc^2" in result
    # The optional label is prefixed with ``eq:`` for consistency
    assert "\\label{eq:mass_energy}" in result
    assert result.strip().endswith("\\end{equation}")


def test_delete_document(client):
    """Users can remove their own documents from the database."""
    # Register and log in
    client.post('/register', data={'username': 'alice', 'password': 'pw'})
    client.post('/login', data={'username': 'alice', 'password': 'pw'})
    # Create a document
    client.post('/documents/new', data={'title': 'Doc', 'content': 'Hello'})
    with app.app_context():
        doc = Document.query.first()
        # Delete the document
        client.post(f'/documents/{doc.id}/delete')
        assert Document.query.count() == 0


def test_delete_document_requires_owner(client):
    """Only the document owner may delete it."""
    # User A creates a document
    client.post('/register', data={'username': 'alice', 'password': 'pw'})
    client.post('/login', data={'username': 'alice', 'password': 'pw'})
    client.post('/documents/new', data={'title': 'Doc', 'content': 'Hello'})
    client.get('/logout')
    # User B attempts deletion
    client.post('/register', data={'username': 'bob', 'password': 'pw'})
    client.post('/login', data={'username': 'bob', 'password': 'pw'})
    with app.app_context():
        doc = Document.query.first()
    res = client.post(f'/documents/{doc.id}/delete')
    assert res.status_code == 403
    # Ensure document still exists
    with app.app_context():
        assert Document.query.count() == 1


def test_profile_menu_links_present(client):
    """Dropdown menu should list profile-related options after login."""
    client.post('/register', data={'username': 'charlie', 'password': 'pw'})
    response = client.post('/login', data={'username': 'charlie', 'password': 'pw'}, follow_redirects=True)
    # The main page after login should include all profile menu options
    assert b'Manage Profiles' in response.data
    assert b'Learning Zone' in response.data
    assert b'My Details' in response.data
    assert b'Subscription Details' in response.data
    assert b'Sign out' in response.data


def test_manage_users_admin_only(client):
    """Only administrators can access the manage users screen."""
    # First registered user becomes admin
    client.post('/register', data={'username': 'admin', 'password': 'pw'})
    client.post('/login', data={'username': 'admin', 'password': 'pw'})
    assert client.get('/manage-users').status_code == 200
    client.get('/logout')
    # A non-admin user should receive a 403 response
    client.post('/register', data={'username': 'dave', 'password': 'pw'})
    client.post('/login', data={'username': 'dave', 'password': 'pw'})
    assert client.get('/manage-users').status_code == 403
