import importlib

import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Flask test client backed by an isolated, freshly-seeded temp DB.

    app.py calls init_db()/seed_db() at import time against the real
    spendly.db, so DB_PATH must be patched before app is (re)imported.
    """
    db_path = tmp_path / "test_spendly.db"

    import database.db as db
    monkeypatch.setattr(db, "DB_PATH", str(db_path))

    import app as app_module
    importlib.reload(app_module)

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def demo_user_id(client):
    import database.db as db
    return db.get_user_by_email("demo@spendly.com")["id"]
