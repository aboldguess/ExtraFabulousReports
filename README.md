# ExtraFabulousReports

ExtraFabulousReports is a lightweight collaborative web application for authoring long-form technical reports in LaTeX. It supports team work, figures and tables, and an administrator-configurable house style.

## Features
- User registration and authentication
- Administrator role for configuring the LaTeX house style
- Create, edit and compile LaTeX documents into PDFs
- Upload images for use in documents
- Dedicated instructions and help pages linked in the navigation bar
- Simple markup for figures with captions and cross-references

## Quick start
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Initialize the database and run the development server:
   ```bash
   flask --app app.py init-db
   flask --app app.py run
   ```
3. Open your browser at http://localhost:5000 and create the first user. The first registered account automatically becomes the administrator.

## Tests
Run the minimal test suite with:
```bash
python -m pytest
```
