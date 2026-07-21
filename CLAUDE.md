# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spendly is a Flask-based expense tracker built as a step-by-step learning project. `app.py` and `database/db.py` contain placeholder comments (e.g. "Students will implement these" / "Students will write this file in Step 1") marking functionality that is intentionally unfinished and built up incrementally in numbered steps (Step 1 = database setup, Step 3 = logout, Step 4 = profile, Step 7-9 = expense CRUD, etc.). When asked to implement a "next step," check the placeholder comments in `app.py` and `database/db.py` first to see what's expected.

There is no lint/format tooling configured in this repo.

## Architecture

- **`app.py`** — single-file Flask app; all routes are defined here as top-level `@app.route` view functions (no blueprints).
- **`database/db.py`** — see `database/CLAUDE.md`.
- **`templates/`** — see `templates/CLAUDE.md`.

Branding: the app name is "Spendly", currency is USD (previously INR — see git history), and page titles follow the `{Page} — Spendly` convention.
