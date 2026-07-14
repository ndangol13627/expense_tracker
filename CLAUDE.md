# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask-based expense tracker built as a step-by-step learning project. `app.py` and `database/db.py` contain placeholder comments (e.g. "Students will implement these" / "Students will write this file in Step 1") marking functionality that is intentionally unfinished and built up incrementally in numbered steps (Step 1 = database setup, Step 3 = logout, Step 4 = profile, Step 7-9 = expense CRUD, etc.). When asked to implement a "next step," check the placeholder comments in `app.py` and `database/db.py` first to see what's expected.

## Commands

```bash
# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dev server (http://localhost:5001)
python app.py

# Run tests
pytest

# Run a single test file / test
pytest tests/test_foo.py
pytest tests/test_foo.py::test_bar
```

There is no lint/format tooling configured in this repo.

## Architecture

- **`app.py`** — single-file Flask app; all routes are defined here as top-level `@app.route` view functions (no blueprints). Currently implemented: `/`, `/register`, `/login`, `/terms`. Stubbed-out routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) return plain placeholder strings and are meant to be built out.
- **`database/db.py`** — intended to hold `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (creates tables with `CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample dev data). Not yet implemented. The SQLite file (`spendly.db`) is gitignored and created locally.
- **`templates/`** — Jinja2 templates. `base.html` is the shared layout (navbar, footer, font/CSS includes) that all pages extend via `{% block title %}` / `{% block content %}` / `{% block scripts %}`. Auth pages (`login.html`, `register.html`) follow a shared `auth-section` / `auth-container` / `auth-card` markup pattern with an `{% if error %}` slot for server-side form errors.
- **`static/css/style.css`** — single global stylesheet for the whole app (no per-page CSS files).
- **`static/js/main.js`** — single global JS file included on every page via `base.html`.

Branding: the app name is "Spendly", currency is USD (previously INR — see git history), and page titles follow the `{Page} — Spendly` convention.
