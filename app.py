"""Main application module for ExtraFabulousReports.

This Flask app lets small teams collaboratively author long-form technical
reports in LaTeX. It features user accounts with optional administrator
privileges, document management, image uploads and PDF compilation using a
configurable LaTeX house style.
"""

import os
import subprocess
from datetime import datetime
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, send_file, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user, UserMixin)
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------------------------------------------------------
# Application configuration
# ----------------------------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me'  # In production use a proper secret!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure an upload directory exists for user images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the database and login manager
# SQLAlchemy models live in the same file for brevity
# ----------------------------------------------------------------------------
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------------------------------------------------------------------
# Database models
# ----------------------------------------------------------------------------

class User(UserMixin, db.Model):
    """Simple user account with optional admin privileges."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Validate a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    """LaTeX document created by a user."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='documents')

class HouseStyle(db.Model):
    """Single-row table storing the LaTeX style/preamble and colour theme."""
    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.Text, default='')
    # Hex colour used for headers, links and buttons across the UI
    primary_color = db.Column(db.String(7), default="#003366")
    # Secondary colour for page background and text
    secondary_color = db.Column(db.String(7), default="#ffffff")

# ----------------------------------------------------------------------------
# Flask-Login configuration
# ----------------------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id: str):
    """Retrieve a user for Flask-Login from the database."""
    return User.query.get(int(user_id))

# ----------------------------------------------------------------------------
# CLI command to initialize the database
# ----------------------------------------------------------------------------

@app.cli.command('init-db')
def init_db():
    """Create database tables and ensure a HouseStyle row with defaults exists."""
    db.create_all()
    if not HouseStyle.query.first():
        # Seed the database with a default colour scheme so templates can render
        db.session.add(HouseStyle(style='',
                                  primary_color="#003366",
                                  secondary_color="#ffffff"))
        db.session.commit()
    print('Database initialized.')

# ----------------------------------------------------------------------------
# Authentication routes
# ----------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration. The first user becomes admin."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            user = User(username=username)
            user.set_password(password)
            # First registered user becomes administrator
            if User.query.count() == 0:
                user.is_admin = True
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate a user and begin a session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('list_documents'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """End the current user session."""
    logout_user()
    return redirect(url_for('login'))

# ----------------------------------------------------------------------------
# Informational routes
# ----------------------------------------------------------------------------

@app.route('/instructions')
def instructions():
    """Display general usage instructions."""
    # Provide a simple page outlining how to use the application
    return render_template('instructions.html')

@app.route('/help')
def help_page():
    """Display a help and troubleshooting page."""
    # Basic guidance and contact information for end users
    return render_template('help.html')

# ----------------------------------------------------------------------------
# Document management routes
# ----------------------------------------------------------------------------

@app.route('/')
@login_required
def index():
    """Redirect to document list once authenticated."""
    return redirect(url_for('list_documents'))

@app.route('/documents')
@login_required
def list_documents():
    """List documents owned by the current user."""
    docs = Document.query.filter_by(author=current_user).all()
    return render_template('document_list.html', documents=docs)

@app.route('/documents/new', methods=['GET', 'POST'])
@login_required
def new_document():
    """Create a new document."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        doc = Document(title=title, content=content, author=current_user)
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('edit_document', doc_id=doc.id))
    return render_template('document_edit.html', document=None)

@app.route('/documents/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    """Edit an existing document."""
    doc = Document.query.get_or_404(doc_id)
    if doc.author != current_user:
        abort(403)
    if request.method == 'POST':
        doc.title = request.form['title']
        doc.content = request.form.get('content', '')
        db.session.commit()
        flash('Document saved')
    return render_template('document_edit.html', document=doc)

@app.route('/documents/<int:doc_id>/compile')
@login_required
def compile_document(doc_id):
    """Compile a document to PDF using pdflatex and return the file."""
    doc = Document.query.get_or_404(doc_id)
    if doc.author != current_user:
        abort(403)
    style = HouseStyle.query.first().style
    # Build a temporary LaTeX file combining style and user content.
    # Each line is concatenated to avoid Python interpreting backslashes as
    # escape sequences.
    tex_source = (
        "\\documentclass{article}\n"
        f"{style}\n"
        "\\begin{document}\n"
        f"{doc.content}\n"
        "\\end{document}"
    )
    tex_path = f'tmp_{doc.id}.tex'
    pdf_path = f'tmp_{doc.id}.pdf'
    with open(tex_path, 'w') as f:
        f.write(tex_source)
    # Run pdflatex; suppress output to keep logs clean
    try:
        subprocess.run(['pdflatex', tex_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        flash(f'Compilation failed: {e}')
        return redirect(url_for('edit_document', doc_id=doc.id))
    return send_file(pdf_path, as_attachment=True)

# ----------------------------------------------------------------------------
# Image upload route
# ----------------------------------------------------------------------------

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle image uploads for inclusion in LaTeX documents."""
    file = request.files['file']
    if not file:
        abort(400)
    filename = file.filename
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    flash(f'Uploaded {filename}. Use path {path} in LaTeX.')
    return redirect(request.referrer or url_for('list_documents'))

# ----------------------------------------------------------------------------
# House style configuration
# ----------------------------------------------------------------------------

@app.route('/style', methods=['GET', 'POST'])
@login_required
def edit_style():
    """Allow the administrator to edit the LaTeX house style and colours."""
    if not current_user.is_admin:
        abort(403)
    style = HouseStyle.query.first()
    if request.method == 'POST':
        style.style = request.form.get('style', '')
        # Persist selected colours so the UI can reflect the configured theme
        style.primary_color = request.form.get('primary_color', style.primary_color)
        style.secondary_color = request.form.get('secondary_color', style.secondary_color)
        db.session.commit()
        flash('Style updated')
    return render_template('style.html', style=style)

# ----------------------------------------------------------------------------
# Template context processors
# ----------------------------------------------------------------------------

@app.context_processor
def inject_user():
    """Make current_user available in all templates."""
    return dict(current_user=current_user)

@app.context_processor
def inject_house_style():
    """Expose the configured house style colours to templates."""
    style = HouseStyle.query.first()
    if not style:
        # Ensure a style row exists even in fresh databases (e.g. tests)
        style = HouseStyle(style='', primary_color="#003366", secondary_color="#ffffff")
        db.session.add(style)
        db.session.commit()
    return dict(house_style=style)

# ----------------------------------------------------------------------------
# Run the application (only when executed directly)
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
