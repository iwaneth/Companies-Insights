import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db_client import fetch_table
from routers import dashboard, features, home

app = FastAPI(debug=False)

app.mount(
    "/static",
    StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")),
    name="static",
)

app.mount(
    "/scripts",
    StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "scripts")),
    name="scripts",
)

app.include_router(home.router) 
app.include_router(dashboard.router)
app.include_router(features.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
@app.get("/healthGG")
async def health():
    """Report healthy only when the API and its Supabase dependency respond."""
    try:
        await asyncio.wait_for(fetch_table("companies", limit=1), timeout=5)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": "unavailable"},
        ) from exc

    return {"status": "ok", "database": "ok"}


@app.get("/status")
async def status():
    return {"status": "ok", "source": "companiesInsights backend"}
