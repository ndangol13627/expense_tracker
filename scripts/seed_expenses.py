import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_db

DESCRIPTIONS = {
    "Food": [
        "Groceries", "Lunch with friends", "Dinner at restaurant", "Swiggy order",
        "Zomato order", "Street food", "Tea and snacks", "Vegetables and fruits",
    ],
    "Transport": [
        "Auto rickshaw", "Ola cab", "Uber ride", "Bus pass", "Petrol",
        "Metro card recharge", "Train ticket", "Bike servicing",
    ],
    "Bills": [
        "Electricity bill", "Water bill", "Mobile recharge", "Internet bill",
        "Gas cylinder", "DTH recharge", "House rent",
    ],
    "Health": [
        "Pharmacy", "Doctor consultation", "Health checkup", "Dental visit",
        "Gym membership",
    ],
    "Entertainment": [
        "Movie tickets", "Netflix subscription", "Concert tickets",
        "Gaming purchase", "Amusement park",
    ],
    "Shopping": [
        "New shoes", "Clothes shopping", "Electronics purchase",
        "Home decor", "Amazon order", "Flipkart order",
    ],
    "Other": [
        "Miscellaneous", "Gift for friend", "Donation", "Stationery",
        "Salon visit",
    ],
}

AMOUNT_RANGES = {
    "Food": (50, 800),
    "Transport": (20, 500),
    "Bills": (200, 3000),
    "Health": (100, 2000),
    "Entertainment": (100, 1500),
    "Shopping": (200, 5000),
    "Other": (50, 1000),
}

CATEGORY_WEIGHTS = {
    "Food": 30,
    "Transport": 20,
    "Bills": 15,
    "Shopping": 15,
    "Other": 10,
    "Entertainment": 5,
    "Health": 5,
}


def random_date_within(months):
    end = datetime.now()
    start = end - timedelta(days=months * 30)
    delta_days = (end - start).days
    random_offset = random.randint(0, max(delta_days, 0))
    return (start + timedelta(days=random_offset)).date()


def generate_expense(user_id, months):
    category = random.choices(
        list(CATEGORY_WEIGHTS.keys()), weights=list(CATEGORY_WEIGHTS.values())
    )[0]
    low, high = AMOUNT_RANGES[category]
    amount = round(random.uniform(low, high), 2)
    description = random.choice(DESCRIPTIONS[category])
    expense_date = random_date_within(months)
    return (user_id, amount, category, expense_date.isoformat(), description)


def main():
    user_id = 2
    count = 5
    months = 3

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            return

        expenses = [generate_expense(user_id, months) for _ in range(count)]

        try:
            conn.execute("BEGIN")
            conn.executemany(
                """INSERT INTO expenses (user_id, amount, category, date, description)
                   VALUES (?, ?, ?, ?, ?)""",
                expenses,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        dates = sorted(e[3] for e in expenses)
        print(f"Inserted {count} expenses for user {user_id}.")
        print(f"Date range: {dates[0]} to {dates[-1]}")
        print("Sample records:")
        for row in conn.execute(
            """SELECT id, amount, category, date, description
               FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5""",
            (user_id,),
        ):
            print(f"  id={row['id']} | {row['date']} | {row['category']:<13} | ${row['amount']:>8} | {row['description']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
