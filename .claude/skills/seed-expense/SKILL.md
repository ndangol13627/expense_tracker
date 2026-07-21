---
name: seed-expense
description: Seeds realistic dummy expense records for a specific Spendly user across a configurable number of past months. Validates the user, reads the database configuration and schema from database/db.py, generates proportionally distributed Indian expense data, and inserts all records in a single transaction. Use this whenever the user asks to create sample expenses, populate test data, seed the Spendly database, or invokes "/seed-expenses <user_id> <count> <months>".
argument-hint: "<user_id> <count> <months>"
allowed-tools:
  - Read
  - Bash(python3:*)
disable-model-invocation: true
---

Read `database/db.py` to understand the expenses table
schema, the database connection pattern, and the database
file name.

User input: `$ARGUMENTS`

---

## Step 1 — Parse Arguments

Extract the following from `$ARGUMENTS`:

- `user_id` — integer
- `count` — integer (number of expenses to generate)
- `months` — integer (number of past months to spread them across)

If any argument is missing or is not a valid integer,
stop immediately and respond with:

> Usage: `/seed-expenses <user_id> <count> <months>`  
> Example: `/seed-expenses 1 50 6`

---

## Step 2 — Verify User Exists

Before generating any data, verify that the supplied
`user_id` exists in the `users` table.

If the user does not exist, stop immediately and respond:

> No user found with id `<user_id>`.

---

## Step 3 — Generate and Insert Expenses

Write and execute a Python script that:

### Data Generation

- Randomly distributes expenses across the previous
  `<months>` months.
- Generates realistic Indian expense descriptions.
- Uses the following categories and amount ranges:

| Category | Amount Range (₹) |
|----------|-----------------:|
| Food | 50–800 |
| Transport | 20–500 |
| Bills | 200–3000 |
| Health | 100–2000 |
| Entertainment | 100–1500 |
| Shopping | 200–5000 |
| Other | 50–1000 |

### Distribution

Generate categories with approximately this weighting:

- Food — highest frequency
- Transport — high
- Shopping — medium
- Bills — medium
- Other — medium
- Entertainment — low
- Health — lowest

### Database Rules

The script must:

- Read and reuse the database connection pattern from
  `database/db.py`.
- **Do not** hardcode the database filename.
- Use **parameterized SQL queries only**.
- Insert all expenses inside a **single database transaction**.
- Roll back the entire transaction if any insert fails.

---

## Step 4 — Confirmation

After the transaction completes successfully, print:

- Total number of inserted expenses
- Date range covered
- Five sample inserted records

If the transaction fails, report the error and confirm
that all inserts were rolled back.

---

## Rules

- Do not modify the database schema.
- Do not create duplicate users.
- Do not hardcode file paths or database names.
- Use realistic descriptions matching each category.
- Keep generated dates within the requested time window.
- Use a single transaction for all inserts.