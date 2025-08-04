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

The project supports both Windows and Linux/Raspberry Pi systems. A small
setup script is provided for Unix-like platforms to make installation
straightforward.

### Linux/macOS/Raspberry Pi
1. **Create a virtual environment and install dependencies**:
   ```bash
   ./setup_extrafabulous_reports_env.sh
   ```
   This script creates a `venv` folder and installs everything from
   `requirements.txt`.
2. **Initialize the database and run the server**:
   ```bash
   python -m flask --app app.py init-db
   ./run_extrafabulous_reports_server.sh
   ```

### Windows
1. **Create a virtual environment**:
   ```powershell
   py -3 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Initialize the database and run the server**:
   ```powershell
   python -m flask --app app.py init-db
   python -m flask --app app.py run-server
   ```

## Running the server

The custom `run-server` command exposes the app on the network. You may select
the port and whether to use the production-ready Waitress server.

```bash
# Development server on port 8000
./run_extrafabulous_reports_server.sh --port 8000

# Production server on default port 5000
./run_extrafabulous_reports_server.sh --prod
```

On Windows use `python -m flask --app app.py run-server` in place of the shell
script.

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
