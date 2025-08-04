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

## Setup

The project supports both Windows and Linux/Raspberry Pi systems. Small helper scripts make installation straightforward.

### Linux/macOS/Raspberry Pi
1. **Create a virtual environment and install dependencies**:
   ```bash
   ./xfabreps_setup_env.sh
   ```
2. **Activate the environment and initialise the database**:
   ```bash
   source venv/bin/activate
   python -m flask --app app.py init-db
   ```
3. **Run the server**:
   ```bash
   ./xfabreps_run_server.sh --port 8000   # choose any port you like
   ```

### Windows
1. **Create a virtual environment and install dependencies**:
   ```powershell
   .\xfabreps_setup_env.ps1
   ```
2. **Activate the environment and initialise the database**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python -m flask --app app.py init-db
   ```
3. **Run the server**:
   ```powershell
   .\xfabreps_run_server.ps1 -Port 8000   # add -Prod to use Waitress
   ```

## Running the server

Both scripts support changing the port and enabling a production-ready Waitress server.

```bash
# Development server on port 8000
./xfabreps_run_server.sh --port 8000

# Production server on default port 5000
./xfabreps_run_server.sh --prod
```

Windows equivalents:
```powershell
# Development server on port 8000
.\xfabreps_run_server.ps1 -Port 8000

# Production server on default port 5000
.\xfabreps_run_server.ps1 -Prod
```

When the server starts it prints the full URL so users know where to connect.

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
