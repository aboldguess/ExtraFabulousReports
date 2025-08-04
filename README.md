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
Follow these steps to get ExtraFabulousReports running. Commands are provided
for both Windows PowerShell and Raspberry Pi/Linux terminals.

1. **Create a virtual environment**
   - *Windows*:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - *Raspberry Pi/Linux*:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the database**
   ```bash
   python -m flask --app app.py init-db
   ```
4. **Start the server**
   - *Windows*:
     ```powershell
     .\XFabReps_windows.ps1 -Port 5000
     ```
   - *Raspberry Pi/Linux*:
     ```bash
     ./XFabReps_rpi.sh -p 5000
     ```
   Append `-Production` or `--production` to use a production-ready server.
   The scripts print a summary so you always know the port and mode.

5. Open your browser at `http://localhost:PORT` (replace `PORT` with your chosen
   value) and create the first user. The first registered account automatically
   becomes the administrator.

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
