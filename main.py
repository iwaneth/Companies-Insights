from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routers import dashboard, home, addingSoon

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(dashboard.router)
app.include_router(addingSoon.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/home")

@app.get("/status")
async def status():
    return {"status": "ok", "source": "CompanyIntelligence backend"}