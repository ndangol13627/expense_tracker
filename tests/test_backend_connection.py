import database.db as db
import database.queries as queries


# ---------------------------------------------------------------- #
# Unit tests — database.queries
# ---------------------------------------------------------------- #

def test_get_user_by_id_returns_profile_dict(client, demo_user_id):
    result = queries.get_user_by_id(demo_user_id)
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    assert result["member_since"]


def test_get_user_by_id_returns_none_for_missing_user(client):
    assert queries.get_user_by_id(999999) is None


def test_get_summary_stats_with_expenses(client, demo_user_id):
    stats = queries.get_summary_stats(demo_user_id)
    assert stats["total_spent"] == 388.25
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_with_no_expenses(client):
    user_id = db.create_user("Fresh User", "fresh@example.com", "password123")
    stats = queries.get_summary_stats(user_id)
    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


def test_get_recent_transactions_with_expenses(client, demo_user_id):
    transactions = queries.get_recent_transactions(demo_user_id)
    assert len(transactions) == 8
    dates = [t["date"] for t in transactions]
    assert dates == sorted(dates, reverse=True)
    for t in transactions:
        assert set(t.keys()) == {"date", "description", "category", "amount"}


def test_get_recent_transactions_with_no_expenses(client):
    user_id = db.create_user("Fresh User Two", "fresh2@example.com", "password123")
    assert queries.get_recent_transactions(user_id) == []


def test_get_category_breakdown_with_expenses(client, demo_user_id):
    breakdown = queries.get_category_breakdown(demo_user_id)
    amounts = [c["amount"] for c in breakdown]
    assert amounts == sorted(amounts, reverse=True)
    assert sum(c["pct"] for c in breakdown) == 100
    assert all(isinstance(c["pct"], int) for c in breakdown)
    assert {c["name"] for c in breakdown} == set(db.CATEGORIES)


def test_get_category_breakdown_with_no_expenses(client):
    user_id = db.create_user("Fresh User Three", "fresh3@example.com", "password123")
    assert queries.get_category_breakdown(user_id) == []


# ---------------------------------------------------------------- #
# Route tests — GET /profile
# ---------------------------------------------------------------- #

def test_profile_redirects_when_logged_out(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_shows_seed_user_data(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})

    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "$388.25" in body
    assert ">8<" in body
    assert "Bills" in body
    for category in db.CATEGORIES:
        assert category in body


def test_profile_shows_zero_state_for_new_user(client):
    client.post("/register", data={
        "name": "New Person",
        "email": "newperson@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    client.post("/login", data={"email": "newperson@example.com", "password": "password123"})

    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "$0.00" in body
