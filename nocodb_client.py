import os
import sqlite3
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()

NOCODB_BASE = os.getenv("NOCODB_BASE_URL")
NOCODB_API_KEY = os.getenv("NOCODB_API_KEY")
NOCODB_SQLITE_PATH = os.getenv("NOCODB_SQLITE_PATH")
NOCODB_TIMEOUT_SECONDS = float(os.getenv("NOCODB_TIMEOUT_SECONDS", "3.0"))


def _build_headers() -> dict[str, str]:
    headers = {}
    if NOCODB_API_KEY:
        headers["xc-token"] = NOCODB_API_KEY
    return headers


def _sqlite_db_file() -> Path | None:
    if not NOCODB_SQLITE_PATH:
        return None

    db_file = Path(NOCODB_SQLITE_PATH)
    if db_file.exists():
        return db_file

    return None


async def fetch_table(project: str, table: str, limit: int = 100):
    if _sqlite_db_file():
        return _fetch_table_from_sqlite(project, table, limit)

    url = f"{NOCODB_BASE}/api/v1/db/data/{project}/{table}?limit={limit}"
    headers = _build_headers()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=NOCODB_TIMEOUT_SECONDS)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        # If the NocoDB REST data endpoint is not available for this install,
        # fall back to reading directly from the local NocoDB sqlite file.
        if exc.response.status_code == 404:
            return _fetch_table_from_sqlite(project, table, limit)
        raise
    except httpx.RequestError:
        # Network / connection issues: try local sqlite fallback
        return _fetch_table_from_sqlite(project, table, limit)


def _fetch_table_from_sqlite(project: str, table: str, limit: int = 100):
    db_file = _sqlite_db_file()
    if not db_file:
        raise FileNotFoundError(f"NocoDB sqlite file not found: {db_file}")

    conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        internal_table = _resolve_internal_table_name(conn, project, table)

        # Ensure the internal table exists
        check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (internal_table,)).fetchone()
        if not check:
            raise FileNotFoundError(f"Table not found in sqlite: {internal_table}")

        cursor = conn.execute(f"SELECT * FROM \"{internal_table}\" LIMIT ?", (limit,))
        rows = cursor.fetchall()
    finally:
        conn.close()

    # convert rows to list[dict]
    out = []
    for r in rows:
        out.append({k: r[k] for k in r.keys()})
    return {"list": out, "pageInfo": {"totalRows": len(out), "pageSize": limit, "page": 1}}


def _normalize_name(value: str) -> str:
    return value.lower().replace("_", " ").strip()


def _resolve_base_id(conn: sqlite3.Connection, project: str) -> str | None:
    row = conn.execute("SELECT id FROM nc_bases_v2 WHERE id = ?", (project,)).fetchone()
    if row:
        return row["id"]

    wanted = _normalize_name(project)
    for row in conn.execute("SELECT id, title FROM nc_bases_v2"):
        if _normalize_name(row["title"] or "") == wanted:
            return row["id"]

    return None


def _resolve_internal_table_name(conn: sqlite3.Connection, project: str, table: str) -> str:
    base_id = _resolve_base_id(conn, project)
    params = [table, table, table]
    base_filter = ""
    if base_id:
        base_filter = "AND base_id = ?"
        params.append(base_id)

    row = conn.execute(
        "SELECT table_name FROM nc_models_v2 "
        "WHERE (id = ? OR table_name = ? OR title = ?) "
        f"{base_filter} "
        "AND type = 'table' AND (deleted = 0 OR deleted IS NULL) "
        "LIMIT 1",
        params,
    ).fetchone()
    if row and row["table_name"]:
        return row["table_name"]

    return table



async def list_projects():
    url = f"{NOCODB_BASE}/api/v1/db/meta/projects"
    headers = _build_headers()

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=NOCODB_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()


def list_project_tables(project: str) -> list[dict[str, str]]:
    db_file = _sqlite_db_file()
    if not db_file:
        raise FileNotFoundError(f"NocoDB sqlite file not found: {db_file}")

    conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        base_id = _resolve_base_id(conn, project) or project
        cursor = conn.execute(
            "SELECT id, table_name, title FROM nc_models_v2 "
            "WHERE base_id = ? AND type = 'table' "
            "AND (deleted = 0 OR deleted IS NULL) "
            "ORDER BY \"order\"",
            (base_id,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row["id"],
            "table_name": row["table_name"],
            "title": row["title"] or row["table_name"],
        }
        for row in rows
    ]
