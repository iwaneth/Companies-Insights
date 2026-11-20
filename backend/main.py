import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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


@app.get("/status")
async def status():
    return {"status": "ok", "source": "companiesInsights backend"}