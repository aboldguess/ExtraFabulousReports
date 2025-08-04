"""Main application module for ExtraFabulousReports.

This Flask app lets small teams collaboratively author long-form technical
reports in LaTeX. It features user accounts with optional administrator
privileges, document management, image uploads and PDF compilation using a
configurable LaTeX house style.
"""

import os
import re
import subprocess
import random  # Used by the lorem ipsum generator
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
# LaTeX helpers
# ----------------------------------------------------------------------------

def render_figures_and_refs(text: str) -> str:
    """Replace custom figure and reference markup with proper LaTeX.

    The editor allows users to insert figures using a compact syntax:

    ``{{figure:path|caption|label}}``

    - ``path`` points to the image file relative to the LaTeX document.
    - ``caption`` is the text displayed below the figure.
    - ``label`` is used for cross-referencing.

    References are written as ``{{ref:label}}`` and expand to
    ``Figure \ref{fig:label}``.

    Parameters
    ----------
    text:
        The raw document content entered by the user.

    Returns
    -------
    str
        The content with all figure and reference markers replaced by
        LaTeX commands ready for compilation.
    """

    # Regular expression matching the custom figure syntax. The pattern
    # captures the path, caption and label segments between the separators.
    figure_pattern = re.compile(r"{{figure:([^|]+)\|([^|]+)\|([^}]+)}}")

    def _figure_repl(match: re.Match) -> str:
        """Build a full LaTeX figure environment from a regex match."""
        path, caption, label = match.groups()
        # The LaTeX environment includes a label with a "fig:" prefix so that
        # references can point to it later.
        return (
            "\\begin{figure}[h]\n"
            "\\centering\n"
            f"\\includegraphics{{{path}}}\n"
            f"\\caption{{{caption}}}\n"
            f"\\label{{fig:{label}}}\n"
            "\\end{figure}\n"
        )

    # Replace all occurrences of the custom figure syntax in the text.
    text = figure_pattern.sub(_figure_repl, text)

    # Substitute reference markers with LaTeX \ref commands. The reference
    # uses the same label supplied in the figure definition above.
    ref_pattern = re.compile(r"{{ref:([^}]+)}}")
    text = ref_pattern.sub(lambda m: f"Figure \\ref{{fig:{m.group(1)}}}", text)

    return text

def build_equation(lhs: str, rhs: str, label: str | None = None) -> str:
    """Construct a LaTeX equation environment from its components.

    Parameters
    ----------
    lhs:
        The left-hand side of the equation.
    rhs:
        The right-hand side of the equation.
    label:
        Optional label for cross-referencing. When provided, a ``\\label``
        statement with an ``eq:`` prefix is included.

    Returns
    -------
    str
        A complete LaTeX ``equation`` environment containing the expression
        and optional label.
    """

    # Combine the left and right expressions into a single equation string.
    equation = f"{lhs} = {rhs}"

    # Build up the lines of the LaTeX ``equation`` environment.
    lines = ["\\begin{equation}", equation]

    # If a label was supplied, append it using the common ``eq:`` prefix so
    # writers can reference the equation later.
    if label:
        lines.append(f"\\label{{eq:{label}}}")

    # Close the environment. Joining the list with newlines keeps the output
    # readable when the LaTeX is inspected directly or embedded in templates.
    lines.append("\\end{equation}")
    return "\n".join(lines)

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


@app.cli.command('run-server')
def run_server():
    """Start the dev server on all interfaces for network access."""
    # Bind to all interfaces so the server is reachable from other devices.
    app.run(host='0.0.0.0', debug=True)

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
# Utility routes
# ----------------------------------------------------------------------------

@app.route('/lorem')
def lorem():
    """Return placeholder Lorem Ipsum text for rapid prototyping."""
    # Canonical set of filler sentences used to assemble paragraphs
    sample_sentences = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    ]
    # Number of paragraphs requested via query parameter; default to one
    paragraphs = int(request.args.get('paras', 1))
    blocks = []
    for _ in range(paragraphs):
        # Build each paragraph from a few random sentences
        sentences = [random.choice(sample_sentences) for _ in range(3)]
        blocks.append(" ".join(sentences))
    # Separate paragraphs with blank lines as expected for plain text
    return "\n\n".join(blocks)

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
    # Convert any custom figure or reference markers into actual LaTeX.
    processed_content = render_figures_and_refs(doc.content)
    # Build a temporary LaTeX file combining style and processed user content.
    # Each line is concatenated to avoid Python interpreting backslashes as
    # escape sequences.
    tex_source = (
        "\\documentclass{article}\n"
        f"{style}\n"
        "\\begin{document}\n"
        f"{processed_content}\n"
        "\\end{document}"
    )
    tex_path = f'tmp_{doc.id}.tex'
    pdf_path = f'tmp_{doc.id}.pdf'
    with open(tex_path, 'w') as f:
        f.write(tex_source)
    # Run pdflatex; suppress output to keep logs clean
    try:
        subprocess.run(
            ['pdflatex', tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        # Provide a helpful error when the LaTeX toolchain is missing
        flash('pdflatex not found. Please install a LaTeX distribution.')
        return redirect(url_for('edit_document', doc_id=doc.id))
    except subprocess.CalledProcessError:
        # Catch compilation errors and surface them to the user
        flash('Compilation failed. Check your LaTeX content for errors.')
        return redirect(url_for('edit_document', doc_id=doc.id))
    return send_file(pdf_path, as_attachment=True)

# ----------------------------------------------------------------------------
# Document deletion route
# ----------------------------------------------------------------------------

@app.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id: int):
    """Remove a document owned by the current user."""
    # Look up the document and ensure the requester owns it; otherwise abort
    doc = Document.query.get_or_404(doc_id)
    if doc.author != current_user:
        abort(403)
    # Delete the document and persist the change
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted')
    return redirect(url_for('list_documents'))

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
    # Allow the user to tweak how the server runs via command-line flags.
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the ExtraFabulousReports web application."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number to listen on (default: 5000).",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Use a production-ready server instead of Flask's development server.",
    )
    args = parser.parse_args()

    # Provide immediate feedback so the user knows how the app is running.
    mode = "production" if args.production else "development"
    print(f"Starting ExtraFabulousReports on port {args.port} in {mode} mode")

    # Listen on all interfaces to allow access from other machines on the network.
    if args.production:
        # Import Waitress lazily so unit tests and basic dev usage don't require it.
        from waitress import serve

        serve(app, host='0.0.0.0', port=args.port)
    else:
        app.run(host='0.0.0.0', port=args.port, debug=True)
