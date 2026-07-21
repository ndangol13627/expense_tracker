"""Tests for the Step 6 "Date Filter" feature on the profile page.

Spec: .claude/specs/06-date-filter-profile.md

These tests exercise `GET /profile` purely through its documented contract —
`date_from` / `date_to` query-string params, the four quick-select presets
rendered in the filter bar, and the resulting summary/transactions/category
sections — without assuming any implementation detail beyond what the spec
describes.

The demo user seeded by `database.db.seed_db()` has all of its expenses
clustered inside the current calendar month, which makes it useless for
testing the month-window presets ("Last 3 Months", "Last 6 Months") in
isolation. The `dated_user` fixture below creates a second user with
expenses spread across 0, 2, 4, and 8 months back so preset/range boundaries
can be exercised unambiguously, regardless of the exact day-level formula a
given preset uses internally.
"""

import calendar
import re
from datetime import date

import pytest

import database.db as db


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def login_demo(client):
    return client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})


def months_ago(d, n):
    """Return the date `n` months before `d`, clamping the day-of-month so
    the result is always valid (e.g. Mar 31 minus 1 month -> Feb 28/29)."""
    month_index = d.month - 1 - n
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def insert_expense(user_id, amount, category, expense_date, description):
    conn = db.get_db()
    try:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, expense_date.isoformat(), description),
        )
        conn.commit()
    finally:
        conn.close()


def extract_preset_url(html, label):
    """Pull the href of the preset <a> tag whose visible text is `label`.

    The filter bar is spec'd to build these links with `url_for("profile",
    date_from=..., date_to=...)`, so we follow the actual rendered link
    rather than hardcoding a date formula ourselves.
    """
    pattern = r'<a href="([^"]+)"[^>]*>\s*' + re.escape(label) + r'\s*</a>'
    match = re.search(pattern, html)
    assert match, f"Could not find a preset link labelled {label!r} in the response body"
    return match.group(1).replace("&amp;", "&")


def get_preset_class(html, label):
    pattern = r'<a href="[^"]+"\s+class="([^"]*)">\s*' + re.escape(label) + r'\s*</a>'
    match = re.search(pattern, html)
    assert match, f"Could not find a preset link labelled {label!r} in the response body"
    return match.group(1)


def is_preset_active(html, label):
    return "filter-preset-active" in get_preset_class(html, label)


def follow_preset(client, label):
    """Load the (unfiltered) profile page, then follow the named preset link."""
    start_body = client.get("/profile").get_data(as_text=True)
    url = extract_preset_url(start_body, label)
    response = client.get(url)
    return response, response.get_data(as_text=True)


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def dated_user(client):
    """A freshly registered, logged-in user with expenses spread across
    several months (this month, -2mo, -4mo, -8mo), used to test preset and
    custom-range boundaries without relying on the demo user's seed data
    (which is entirely inside the current calendar month).
    """
    today = date.today()
    user_id = db.create_user("Dated User", "dated@example.com", "password123")

    expenses = {
        "this_month": (50.00, "Food", today, "ThisMonthExpense"),
        "two_months_ago": (75.00, "Transport", months_ago(today, 2), "TwoMonthsAgoExpense"),
        "four_months_ago": (90.00, "Bills", months_ago(today, 4), "FourMonthsAgoExpense"),
        "eight_months_ago": (60.00, "Health", months_ago(today, 8), "EightMonthsAgoExpense"),
    }
    for amount, category, expense_date, description in expenses.values():
        insert_expense(user_id, amount, category, expense_date, description)

    client.post("/login", data={"email": "dated@example.com", "password": "password123"})

    return {"user_id": user_id, "today": today, "expenses": expenses}


# ------------------------------------------------------------------ #
# Auth guard
# ------------------------------------------------------------------ #

@pytest.mark.parametrize(
    "query_string",
    [
        "",
        "date_from=2026-01-01&date_to=2026-01-31",
        "date_from=not-a-date",
        "date_from=2026-08-01&date_to=2026-01-01",
    ],
    ids=["no_params", "valid_range", "malformed", "from_after_to"],
)
def test_profile_redirects_to_login_when_logged_out_regardless_of_date_params(client, query_string):
    url = "/profile" + (f"?{query_string}" if query_string else "")
    response = client.get(url)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# ------------------------------------------------------------------ #
# Happy path — no filter (unchanged from Step 5)
# ------------------------------------------------------------------ #

def test_no_query_params_matches_unfiltered_step5_baseline(client):
    login_demo(client)
    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "$388.25" in body
    assert ">8<" in body
    assert "Bills" in body


def test_no_filter_marks_all_time_preset_active(client):
    login_demo(client)
    body = client.get("/profile").get_data(as_text=True)

    assert is_preset_active(body, "All Time")
    assert not is_preset_active(body, "This Month")
    assert not is_preset_active(body, "Last 3 Months")
    assert not is_preset_active(body, "Last 6 Months")


def test_no_filter_leaves_custom_range_inputs_empty(client):
    login_demo(client)
    body = client.get("/profile").get_data(as_text=True)

    assert 'id="date_from" name="date_from" class="form-input" value=""' in body
    assert 'id="date_to" name="date_to" class="form-input" value=""' in body


# ------------------------------------------------------------------ #
# Happy path — presets
# ------------------------------------------------------------------ #

def test_this_month_preset_filters_all_sections_to_current_calendar_month(client, dated_user):
    response, body = follow_preset(client, "This Month")

    assert response.status_code == 200
    assert "$50.00" in body
    assert ">1<" in body
    assert "ThisMonthExpense" in body
    assert "TwoMonthsAgoExpense" not in body
    assert "FourMonthsAgoExpense" not in body
    assert "EightMonthsAgoExpense" not in body
    assert is_preset_active(body, "This Month")
    assert not is_preset_active(body, "Last 3 Months")
    assert not is_preset_active(body, "Last 6 Months")
    assert not is_preset_active(body, "All Time")


def test_last_3_months_preset_filters_to_three_month_window(client, dated_user):
    response, body = follow_preset(client, "Last 3 Months")

    assert response.status_code == 200
    assert "$125.00" in body
    assert ">2<" in body
    assert "ThisMonthExpense" in body
    assert "TwoMonthsAgoExpense" in body
    assert "FourMonthsAgoExpense" not in body
    assert "EightMonthsAgoExpense" not in body
    assert is_preset_active(body, "Last 3 Months")
    assert not is_preset_active(body, "This Month")
    assert not is_preset_active(body, "Last 6 Months")
    assert not is_preset_active(body, "All Time")


def test_last_6_months_preset_filters_to_six_month_window(client, dated_user):
    response, body = follow_preset(client, "Last 6 Months")

    assert response.status_code == 200
    assert "$215.00" in body
    assert ">3<" in body
    assert "ThisMonthExpense" in body
    assert "TwoMonthsAgoExpense" in body
    assert "FourMonthsAgoExpense" in body
    assert "EightMonthsAgoExpense" not in body
    assert is_preset_active(body, "Last 6 Months")
    assert not is_preset_active(body, "This Month")
    assert not is_preset_active(body, "Last 3 Months")
    assert not is_preset_active(body, "All Time")


def test_all_time_preset_clears_an_active_filter_and_shows_all_expenses(client, dated_user):
    # Apply an unrelated filter first, then click "All Time" to clear it.
    filtered_body = client.get("/profile?date_from=1990-01-01&date_to=1990-01-31").get_data(as_text=True)
    url = extract_preset_url(filtered_body, "All Time")

    response = client.get(url)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "$275.00" in body
    assert ">4<" in body
    assert "ThisMonthExpense" in body
    assert "TwoMonthsAgoExpense" in body
    assert "FourMonthsAgoExpense" in body
    assert "EightMonthsAgoExpense" in body
    assert is_preset_active(body, "All Time")


def test_all_time_preset_link_has_no_query_params(client):
    login_demo(client)
    body = client.get("/profile").get_data(as_text=True)
    url = extract_preset_url(body, "All Time")

    assert "?" not in url, "All Time preset must be a clean /profile URL with no query params"


# ------------------------------------------------------------------ #
# Happy path — custom valid date range
# ------------------------------------------------------------------ #

def test_custom_valid_date_range_shows_only_expenses_within_range(client, dated_user):
    date_from = dated_user["expenses"]["four_months_ago"][2].isoformat()
    date_to = dated_user["expenses"]["two_months_ago"][2].isoformat()

    response = client.get(f"/profile?date_from={date_from}&date_to={date_to}")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "TwoMonthsAgoExpense" in body
    assert "FourMonthsAgoExpense" in body
    assert "ThisMonthExpense" not in body
    assert "EightMonthsAgoExpense" not in body


def test_custom_range_is_reflected_in_filter_inputs_and_marked_active(client, dated_user):
    date_from = dated_user["expenses"]["four_months_ago"][2].isoformat()
    date_to = dated_user["expenses"]["two_months_ago"][2].isoformat()

    body = client.get(f"/profile?date_from={date_from}&date_to={date_to}").get_data(as_text=True)

    assert f'value="{date_from}"' in body
    assert f'value="{date_to}"' in body
    assert "filter-custom-active" in body
    for label in ("This Month", "Last 3 Months", "Last 6 Months", "All Time"):
        assert not is_preset_active(body, label), f"{label} should not be active for a non-matching custom range"


# ------------------------------------------------------------------ #
# DB-side-effect-style checks — all three sections scoped consistently
# ------------------------------------------------------------------ #

def test_custom_range_scopes_summary_transactions_and_categories_together(client, dated_user):
    date_from = dated_user["expenses"]["four_months_ago"][2].isoformat()
    date_to = dated_user["expenses"]["two_months_ago"][2].isoformat()

    body = client.get(f"/profile?date_from={date_from}&date_to={date_to}").get_data(as_text=True)

    # Summary stats: only Transport (75.00) + Bills (90.00) = 165.00, 2 txns, top = Bills
    assert "$165.00" in body
    assert ">2<" in body

    # Transaction list: only the two in-range expenses
    assert "TwoMonthsAgoExpense" in body
    assert "FourMonthsAgoExpense" in body
    assert "ThisMonthExpense" not in body
    assert "EightMonthsAgoExpense" not in body

    # Category breakdown: only Transport and Bills, with their in-range amounts
    assert "Transport" in body
    assert "$75.00" in body
    assert "$90.00" in body
    assert "Food" not in body
    assert "Health" not in body


# ------------------------------------------------------------------ #
# Validation errors
# ------------------------------------------------------------------ #

def test_date_from_after_date_to_flashes_error_and_falls_back_to_unfiltered(client):
    login_demo(client)
    response = client.get("/profile?date_from=2026-08-01&date_to=2026-01-01")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Start date must be before end date." in body
    # Falls back to the full unfiltered dataset
    assert "$388.25" in body
    assert ">8<" in body
    assert "Bills" in body


@pytest.mark.parametrize(
    "query_string",
    [
        "date_from=not-a-date&date_to=2026-01-31",
        "date_from=2026-01-01&date_to=not-a-date",
        "date_from=2026-01-01",
        "date_to=2026-01-31",
        "date_from=2026-13-45&date_to=2026-01-31",
    ],
    ids=[
        "malformed_date_from",
        "malformed_date_to",
        "only_date_from_given",
        "only_date_to_given",
        "impossible_calendar_date",
    ],
)
def test_malformed_or_partial_date_params_silently_fall_back_to_unfiltered(client, query_string):
    login_demo(client)
    response = client.get(f"/profile?{query_string}")
    body = response.get_data(as_text=True)

    assert response.status_code == 200, "Malformed/partial date params must not crash the app"
    assert "$388.25" in body
    assert ">8<" in body
    assert "Bills" in body
    assert 'class="flash-messages"' not in body, "Malformed/partial params must fall back silently, without a flash message"


# ------------------------------------------------------------------ #
# Edge case — zero matching expenses
# ------------------------------------------------------------------ #

def test_date_range_with_no_matching_expenses_shows_zero_state(client, dated_user):
    response = client.get("/profile?date_from=1990-01-01&date_to=1990-01-31")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "$0.00" in body
    assert ">0<" in body
    assert "No transactions yet." in body
    assert "No spending data yet." in body
    for description in (
        "ThisMonthExpense",
        "TwoMonthsAgoExpense",
        "FourMonthsAgoExpense",
        "EightMonthsAgoExpense",
    ):
        assert description not in body
    assert 'class="flash-messages"' not in body, "An empty result set is not an error condition"


# ------------------------------------------------------------------ #
# Currency — $ everywhere, never a stray rupee symbol
# ------------------------------------------------------------------ #

def test_amounts_use_dollar_sign_never_rupee_symbol(client, dated_user):
    date_from = dated_user["expenses"]["four_months_ago"][2].isoformat()
    date_to = dated_user["expenses"]["two_months_ago"][2].isoformat()

    urls = [
        "/profile",  # unfiltered
        "/profile?date_from=1990-01-01&date_to=1990-01-31",  # zero-match filtered
        f"/profile?date_from={date_from}&date_to={date_to}",  # custom range
    ]
    for url in urls:
        body = client.get(url).get_data(as_text=True)
        assert "₹" not in body, f"Found a stray rupee symbol in response for {url}"
        assert "$" in body, f"Expected a dollar sign in response for {url}"
