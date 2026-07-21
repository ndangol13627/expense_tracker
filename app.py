import sqlite3
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from werkzeug.security import check_password_hash

from database.db import init_db, seed_db, create_user, get_user_by_email
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

with app.app_context():
    init_db()
    seed_db()

CATEGORY_SLUGS = {
    "Food": "food",
    "Transport": "transport",
    "Bills": "bills",
    "Health": "health",
    "Entertainment": "entertainment",
    "Shopping": "shopping",
    "Other": "other",
}

MAX_TRANSACTIONS_SHOWN = 10


def _parse_iso_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _month_start(d, months_back):
    """First day of the month that is `months_back` months before d's month."""
    month_index = d.month - 1 - months_back
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _build_filters(today, active_from, active_to, date_from_raw, date_to_raw):
    presets_spec = [
        ("This Month", _month_start(today, 0), today),
        ("Last 3 Months", _month_start(today, 2), today),
        ("Last 6 Months", _month_start(today, 5), today),
    ]
    presets = []
    for label, preset_from, preset_to in presets_spec:
        preset_from_str, preset_to_str = preset_from.isoformat(), preset_to.isoformat()
        presets.append({
            "label": label,
            "url": url_for("profile", date_from=preset_from_str, date_to=preset_to_str),
            "active": active_from == preset_from_str and active_to == preset_to_str,
        })
    presets.append({
        "label": "All Time",
        "url": url_for("profile"),
        "active": active_from is None and active_to is None,
    })

    return {
        "presets": presets,
        "date_from": date_from_raw,
        "date_to": date_to_raw,
        "custom_active": bool(active_from) and not any(p["active"] for p in presets),
    }


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
            return render_template("register.html")

        flash("Account created. Please sign in.", "success")
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("register.html")

    abort(405)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    abort(405)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile", methods=["GET"])
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    profile_user = get_user_by_id(session["user_id"])
    if profile_user is None:
        session.clear()
        return redirect(url_for("login"))

    user = {
        "name": profile_user["name"],
        "email": profile_user["email"],
        "initials": "".join(part[0] for part in profile_user["name"].split()[:2]).upper(),
        "member_since": profile_user["member_since"],
    }

    date_from_raw = request.args.get("date_from", "")
    date_to_raw = request.args.get("date_to", "")
    date_from_obj = _parse_iso_date(date_from_raw)
    date_to_obj = _parse_iso_date(date_to_raw)

    active_from, active_to = None, None
    if date_from_obj and date_to_obj:
        if date_from_obj > date_to_obj:
            flash("Start date must be before end date.", "error")
        else:
            active_from, active_to = date_from_raw, date_to_raw

    summary = get_summary_stats(session["user_id"], date_from=active_from, date_to=active_to)
    stats = [
        {"label": "Total spent", "value": f"${summary['total_spent']:,.2f}"},
        {"label": "Transactions", "value": str(summary["transaction_count"])},
        {"label": "Top category", "value": summary["top_category"]},
    ]

    transactions = []
    for row in get_recent_transactions(
        session["user_id"], limit=MAX_TRANSACTIONS_SHOWN, date_from=active_from, date_to=active_to
    ):
        row_date = datetime.strptime(row["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        slug = CATEGORY_SLUGS.get(row["category"], "other")
        transactions.append({
            "date": row_date,
            "description": row["description"] or "—",
            "category": row["category"],
            "amount": f"${row['amount']:,.2f}",
            "badge_class": f"cat-badge-{slug}",
        })

    categories = []
    for cat in get_category_breakdown(session["user_id"], date_from=active_from, date_to=active_to):
        slug = CATEGORY_SLUGS.get(cat["name"], "other")
        width_percent = round(cat["pct"] / 5) * 5
        categories.append({
            "name": cat["name"],
            "amount": f"${cat['amount']:,.2f}",
            "percent": cat["pct"],
            "bar_class": f"cat-bar-{slug}",
            "width_class": f"bar-w-{width_percent}",
        })

    filters = _build_filters(date.today(), active_from, active_to, date_from_raw, date_to_raw)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        transaction_count=summary["transaction_count"],
        transactions_shown=len(transactions),
        filters=filters,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
