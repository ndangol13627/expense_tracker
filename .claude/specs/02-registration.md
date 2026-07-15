# Spec: Registration

## Overview
This step implements working user registration for Spendly. Currently `/register` only renders `register.html` on GET with no form handling — submitting the form does nothing. This feature adds POST handling that validates the submitted name/email/password, hashes the password with werkzeug, inserts a new row into the `users` table, and starts a logged-in session. It builds directly on the database layer from Step 1 and is a prerequisite for login (session-based auth), logout (Step 3), and profile (Step 4).

## Depends on
- Step 1 — Database setup (`database/db.py`: `get_db()`, `users` table)

## Routes
- `GET /register` — render the registration form — public (already implemented, unchanged)
- `POST /register` — validate input, create the user, start session, redirect to a logged-in page — public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email` UNIQUE, `password_hash`, `created_at`) already supports registration as defined in `database/db.py`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — render `{{ error }}` (already supported via `{% if error %}`) when validation fails or email is already taken; repopulate `name`/`email` field values after a failed submit so the user doesn't retype them

## Files to change
- `app.py` — implement `POST` handling on the `/register` route: read form fields, validate, check for duplicate email, hash password, insert user, set session, redirect
- `templates/register.html` — repopulate `name`/`email` values on validation failure

## Files to create
None

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate required fields server-side even though the form has `required` attributes (client-side validation is not a substitute)
- Check for existing email before inserting; on conflict, re-render `register.html` with an `error` message instead of a raw SQLite `IntegrityError`
- Use Flask's `session` for login state (no separate session table)
- Redirect (`302`) after a successful POST — never render a success page directly from a POST handler

## Definition of done
- [ ] Submitting the registration form with valid, unique name/email/password creates a row in `users` with a hashed (not plaintext) password
- [ ] After successful registration, the browser is redirected and the user is logged in (session is set)
- [ ] Submitting with an email that already exists re-renders `register.html` with a visible error and does not create a duplicate row
- [ ] Submitting with a missing required field re-renders `register.html` with a visible error and does not create a row
- [ ] Submitted `name`/`email` values are preserved in the form fields after a failed submission
- [ ] No plaintext password ever appears in the database or logs
- [ ] App starts and `/register` still renders correctly on GET
