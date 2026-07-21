---
name: seed-user
description: Creates one realistic dummy Indian user in the Spendly database. Reads the users table schema and database connection pattern from database/db.py, generates a unique name and email, securely hashes the default password, inserts the user, and prints the created user details. Use this when the user asks to create a sample user, seed a test account, populate the users table, or invokes "/create-dummy-user".
allowed-tools:
  - Read
  - Bash(python3:*)
disable-model-invocation: true
---

Read `database/db.py` to understand the `users` table schema and the `get_db()` helper.

Then write and run a Python script using Bash that:

## Step 1 — Generate a Dummy User

Generate one realistic random Indian user using common names from different regions of India.

Create:

- `name` — realistic Indian first and last name
- `email` — derived from the name with a random two- or three-digit suffix
- `password` — `password123`, hashed with Werkzeug
- `created_at` — current date and time

Example email:

`rahul.sharma91@gmail.com`

Use:

```python
from werkzeug.security import generate_password_hash
```

Never store the plain-text password in the database.

## Step 2 — Ensure the Email Is Unique

Before inserting the user:

1. Check whether the generated email already exists in the `users` table.
2. Use a parameterized SQL query.
3. If the email exists, generate a new numeric suffix.
4. Repeat until a unique email is found.

Use a reasonable retry limit to prevent an infinite loop.

## Step 3 — Insert the User

Insert the user using the same `get_db()` pattern found in `database/db.py`.

Requirements:

- Do not hardcode the database filename.
- Match the existing `users` table schema.
- Use parameterized SQL queries only.
- Commit only after the insert succeeds.
- Roll back the transaction if the insert fails.
- Allow the database to generate the user ID if the schema uses an auto-incrementing primary key.

## Step 4 — Print Confirmation

After the user is created successfully, print:

```text
Dummy user created successfully.

ID: <id>
Name: <name>
Email: <email>
```

Do not print the password hash.

## Rules

- Create exactly one user.
- Do not modify the database schema.
- Do not modify existing users.
- Do not create duplicate emails.
- Do not hardcode the database path or filename.
- Use the existing `get_db()` helper.
- Use parameterized SQL queries only.
- Hash the password using Werkzeug.
- Do not make unrelated file changes.