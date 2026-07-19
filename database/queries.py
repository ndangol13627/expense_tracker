from datetime import datetime

from database.db import get_user_by_id as _get_user_row, get_expenses_by_user


def get_user_by_id(user_id):
    row = _get_user_row(user_id)
    if row is None:
        return None

    created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created_at.strftime("%B %Y"),
    }


def get_summary_stats(user_id):
    expenses = get_expenses_by_user(user_id)

    total_spent = sum(row["amount"] for row in expenses)
    transaction_count = len(expenses)

    category_totals = {}
    for row in expenses:
        category_totals[row["category"]] = category_totals.get(row["category"], 0) + row["amount"]

    top_category = max(category_totals, key=category_totals.get) if category_totals else "—"

    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category,
    }


def get_recent_transactions(user_id, limit=10):
    expenses = get_expenses_by_user(user_id)
    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"],
        }
        for row in expenses[:limit]
    ]


def get_category_breakdown(user_id):
    expenses = get_expenses_by_user(user_id)
    if not expenses:
        return []

    category_totals = {}
    for row in expenses:
        category_totals[row["category"]] = category_totals.get(row["category"], 0) + row["amount"]

    total_spent = sum(category_totals.values())
    ordered = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)

    # Round every category except the largest, then let the largest absorb
    # whatever remainder is needed so the percentages sum to exactly 100.
    rounded_rest = [round((amount / total_spent) * 100) for _, amount in ordered[1:]]
    largest_pct = 100 - sum(rounded_rest)
    pcts = [largest_pct] + rounded_rest

    return [
        {"name": category, "amount": amount, "pct": pct}
        for (category, amount), pct in zip(ordered, pcts)
    ]
