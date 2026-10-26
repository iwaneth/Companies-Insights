import asyncio
from types import SimpleNamespace

from backend import db_client


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.table_name = None
        self.limit_value = None

    def table(self, table_name):
        self.table_name = table_name
        return self

    def select(self, columns):
        assert columns == "*"
        return self

    def limit(self, limit):
        self.limit_value = limit
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


def test_fetch_table_returns_supabase_rows_and_pagination(monkeypatch):
    query = FakeQuery([{"companyName": "Example"}])
    class FakeClient:
        def table(self, table_name):
            return query.table(table_name)

    client = FakeClient()
    monkeypatch.setattr(db_client, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(db_client, "SUPABASE_SECRET_KEY", "server-secret")
    monkeypatch.setattr("supabase.create_client", lambda url, key: client)

    result = asyncio.run(db_client.fetch_table("companies", limit=25))

    assert query.table_name == "companies"
    assert query.limit_value == 25
    assert result == {
        "list": [{"companyName": "Example"}],
        "pageInfo": {"totalRows": 1, "pageSize": 25, "page": 1},
    }


def test_fetch_table_requires_server_secret(monkeypatch):
    monkeypatch.setattr(db_client, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(db_client, "SUPABASE_SECRET_KEY", None)

    try:
        asyncio.run(db_client.fetch_table("companies"))
    except RuntimeError as error:
        assert "SUPABASE_SECRET_KEY" in str(error)
    else:
        raise AssertionError("Expected missing server secret to raise RuntimeError")
