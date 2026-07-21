---
name: create-spec
description: Creates a new Spendly feature specification and corresponding Git feature branch by validating the repository state, researching the existing codebase and roadmap, generating a structured implementation spec, and saving it under .claude/specs/. Use this whenever the user wants to start a new Spendly feature, create a spec, initialize a feature branch, or invokes "/create-feature-spec <step-number> <feature-name>".
argument-hint: "<step-number> <feature-name> e.g. 2 registration"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(git:*)
disable-model-invocation: true
---

You are a senior developer spinning up a new feature for the
Spendly expense tracker.

Always follow the rules defined in `CLAUDE.md`.

User input:

`$ARGUMENTS`

---

# Step 1 — Verify Working Directory

Run:

```bash
git status
```

If there are any:

- Modified files
- Staged changes
- Untracked files

stop immediately and respond:

> Your working directory is not clean. Please commit, stash, or discard your changes before creating a new feature branch.

Do **not** continue until the working directory is clean.

---

# Step 2 — Parse Arguments

Extract the following from `$ARGUMENTS`:

## 1. Step Number

Convert to two digits.

Examples:

- `2` → `02`
- `9` → `09`
- `11` → `11`

## 2. Feature Title

Human-readable title in Title Case.

Examples:

- Registration
- Login and Logout
- Monthly Reports

## 3. Feature Slug

Create a Git-safe slug.

Requirements:

- lowercase
- kebab-case
- only `a-z`, `0-9`, and `-`
- maximum 40 characters

Examples:

- registration
- login-logout
- monthly-reports

## 4. Branch Name

Use:

```
feature/<feature-slug>
```

Example:

```
feature/registration
```

If the arguments cannot be parsed confidently, ask the user for clarification before proceeding.

---

# Step 3 — Ensure Branch Name Is Available

Run:

```bash
git branch
```

If the branch already exists, append an incrementing suffix.

Examples:

```
feature/registration-01
feature/registration-02
```

Choose the first available branch name.

---

# Step 4 — Update Main

Run:

```bash
git checkout main
git pull origin main
```

If either command fails, stop and report the error.

---

# Step 5 — Create the Feature Branch

Run:

```bash
git checkout -b <branch_name>
```

Confirm that the new branch was created successfully before continuing.

---

# Step 6 — Research the Codebase

Read the following before generating the specification:

- `CLAUDE.md`
- `app.py`
- `database/db.py`
- Every specification inside `.claude/specs/`

During research:

- Understand the current roadmap.
- Review existing routes.
- Review the current database schema.
- Review existing conventions.
- Avoid duplicating previous specifications.

If `CLAUDE.md` indicates the requested step has already been completed, stop and notify the user.

---

# Step 7 — Generate the Specification

Create a specification with the following structure exactly.

```md
# Spec: <feature_title>

## Overview

...

## Depends on

...

## Routes

...

## Database changes

...

## Templates

### Create

...

### Modify

...

## Files to change

...

## Files to create

...

## New dependencies

...

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterized queries only
- Passwords hashed with Werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html

## Definition of done

- ...
```

Requirements:

- Verify database changes against `database/db.py`.
- If no new routes are required, explicitly write **"No new routes."**
- If no database changes are required, explicitly write **"No database changes."**
- If no new dependencies are required, explicitly write **"No new dependencies."**
- The Definition of Done must contain concrete, testable checklist items.

---

# Step 8 — Save the Specification

Save the document as:

```
.claude/specs/<step_number>-<feature_slug>.md
```

Verify the file was created successfully.

---

# Step 9 — Report

Print exactly:

```text
Branch:    <branch_name>
Spec file: .claude/specs/<step_number>-<feature_slug>.md
Title:     <feature_title>
```

Then print:

> Review the spec at `.claude/specs/<step_number>-<feature_slug>.md` then enter Plan Mode with **Shift+Tab twice** to begin implementation.

Do **not** print the contents of the specification unless the user explicitly requests it.

---

# Rules

- Always start from a clean Git working tree.
- Always update `main` before creating a feature branch.
- Never overwrite an existing specification.
- Never overwrite an existing branch.
- Research the existing roadmap before writing a new spec.
- Keep the specification implementation-focused and testable.
- Do not modify application code.
- Do not implement the feature.
- Do not print the generated specification unless requested.