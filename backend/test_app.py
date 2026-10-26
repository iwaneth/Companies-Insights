from fastapi.testclient import TestClient

try:
    from main import app
except ImportError:  # pragma: no cover - package-style test invocation
    from backend.main import app

def test_health_check():
    response = TestClient(app).get("/status")
    assert response.status_code == 200


def test_dashboard_renders_each_row_from_all_supabase_tables(monkeypatch):
    from routers import dashboard as dashboard_router

    table_names = (
        "companies",
        "halfDynamicProperties",
        "companyProfile",
        "companyNews",
    )
    calls = []

    rows_by_table = {
        "companies": [{"id": 7, "companyName": "Example Corp"}],
        "halfDynamicProperties": [
            {"id": 2, "company_id": 7, "employees": "50"}
        ],
        "companyProfile": [
            {"id": 3, "company_id": 7, "profile": "Example profile"}
        ],
        "companyNews": [
            {"id": 4, "company_id": 7, "title": "Example news"}
        ],
    }

    async def fake_fetch_table(table):
        calls.append(table)
        return {"list": rows_by_table[table]}

    monkeypatch.setattr(dashboard_router, "fetch_table", fake_fetch_table)

    response = TestClient(app).get("/dashboard")

    assert response.status_code == 200
    assert calls == list(table_names)
    assert "Example Corp" in response.text
    assert "50" in response.text
    assert "Example profile" in response.text
    assert "Example news" in response.text

