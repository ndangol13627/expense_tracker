# Spec: Login and Logout

## Overview
Implement session-based authentication so registered users can sign in and out of Spendly. This step upgrades the existing stub `GET /login` route into a full login flow that verifies credentials against the `users` table and starts a Flask session, and upgrades the `/logout` placeholder to clear that session. It also updates the navbar so it reflects whether a visitor is signed in. This is the gate that all future authenticated features (profile, expense CRUD) will depend on.

## Depends on
- Step 01 — Database setup (`users` table, `get_db()`)
- Step 02 — Registration (`create_user()`, working `/register` flow to produce accounts to log into)

## Routes
- `GET /login` — render login form — public; if already authenticated, redirect to `/`
- `POST /login` — verify email/password, start session, redirect to `/` — public
- `GET /logout` — clear session, redirect to landing page — logged-in
- `GET /register`, `POST /register` — if already authenticated, redirect to `/` before any other handling (guards against a logged-in user re-registering or re-visiting the login form)

## Database changes
No new tables or columns. The existing `users` table (id, name, email, password_hash, created_at) covers all requirements.

A new DB helper must be added to `database/db.py`:
- `get_user_by_email(email)` — returns the matching row from `users` (or `None`) so the login route can verify the password hash.

## Templates
- **Modify**: `templates/login.html`
  - Change the form `action` to `url_for('login')` with `method="post"` (currently hardcoded to `/login`)
  - Add a block to display a flash/error message on invalid credentials, matching the `auth-error` pattern already used in `register.html`
  - Keep all existing visual design
- **Modify**: `templates/base.html`
  - Update `.nav-links` to conditionally show "Sign in" / "Get started" when logged out, or the user's name + "Sign out" (`url_for('logout')`) when logged in, based on `session.get('user_id')`

## Files to change
- `app.py` — upgrade `login()` to handle `GET` and `POST`; add session creation, flash + redirect logic; upgrade `logout()` to clear the session and redirect
- `database/db.py` — add `get_user_by_email()` helper
- `templates/login.html` — wire up form action/method and flash message display
- `templates/base.html` — conditional navbar based on session state

## Files to create
None.

## New dependencies
No new dependencies. Uses Flask's built-in `session`, `flash`, `redirect`, and `url_for`, and `werkzeug.security.check_password_hash` (werkzeug already installed).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Verify passwords with `werkzeug.security.check_password_hash` — never compare plaintext
- Store only `user_id` (and optionally `name`) in the Flask `session` — never store the password hash in the session
- Server-side validation must check:
  1. Both fields are non-empty
  2. Email exists in `users`
  3. Password matches the stored hash
- On any validation failure, re-render the form with a flashed error message (e.g. "Invalid email or password") — do not redirect, and do not reveal whether the email or the password was wrong
- On success, `flash` a success message and `redirect` to `url_for('landing')`
- `/logout` must clear the entire session (`session.clear()`) and redirect to `url_for('landing')`
- Use `abort(405)` if an unsupported HTTP method reaches `/login`
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs


## Definition of done
- [x] Visiting `GET /login` renders the login form with email and password fields
- [x] Submitting the form with valid credentials (e.g. demo@spendly.com / demo123) sets `session["user_id"]` and redirects to `/`
- [x] Submitting with a wrong password shows "Invalid email or password." flash and stays on the login page
- [x] Submitting with an unregistered email shows the same generic error flash
- [x] Visiting `GET /logout` clears the session and redirects to `/`
- [x] After logout, `session["user_id"]` is no longer present
- [x] The `/logout` route no longer returns the raw stub string
- [x] Visiting `GET /login` or `GET /register` while already authenticated redirects to `/` instead of rendering the form
