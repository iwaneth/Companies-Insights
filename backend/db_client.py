import asyncio
from typing import Any

try:
    from config import SUPABASE_SECRET_KEY, SUPABASE_URL
except ImportError:  # pragma: no cover - package-style imports
    from backend.config import SUPABASE_SECRET_KEY, SUPABASE_URL


def _fetch_table(table: str, limit: int) -> dict[str, Any]:
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_SECRET_KEY in the backend environment."
        )

    from supabase import create_client

    client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    rows = client.table(table).select("*").limit(limit).execute().data
    return {
        "list": rows,
        "pageInfo": {"totalRows": len(rows), "pageSize": limit, "page": 1},
    }


async def fetch_table(table: str, limit: int = 100) -> dict[str, Any]:
    return await asyncio.to_thread(_fetch_table, table, limit)