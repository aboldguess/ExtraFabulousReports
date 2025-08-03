# ExtraFabulousReports

ExtraFabulousReports is a lightweight collaborative web application for authoring long-form technical reports in LaTeX. It supports team work, figures and tables, and an administrator-configurable house style.

## Features
- User registration and authentication
- Administrator role for configuring the LaTeX house style
- Create, edit and compile LaTeX documents into PDFs
- Upload images for use in documents
- Dedicated instructions and help pages linked in the navigation bar
- Simple markup for figures with captions and cross-references
- Helper to programmatically build LaTeX equation blocks

## Quick start
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Initialize the database and run the development server:
   ```bash
   python -m flask --app app.py init-db
   # Bind to all interfaces so the app is reachable from other devices on the
   # network.
   python -m flask --app app.py run --host=0.0.0.0
   ```
   The `python -m flask` form ensures the CLI is available even if the `flask`
   executable is not on your system's `PATH`, which is common on Windows.
3. Open your browser at http://localhost:5000 (or replace `localhost` with the server's IP address from another device) and create the first user. The first registered account automatically becomes the administrator.

## Tests
Run the minimal test suite with:
```bash
python -m pytest
```

## Equation builder example
Generate a LaTeX equation environment from Python code:

```python
from app import build_equation

latex = build_equation("E", "mc^2", label="mass_energy")
print(latex)
```

This prints:

```
\begin{equation}
E = mc^2
\label{eq:mass_energy}
\end{equation}
```
