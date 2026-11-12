from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)
 
# @router.get("/home", response_class=HTMLResponse)
# async def home(request: Request):
    # return render("home.html", request) -- disabled temporary


@router.get("/home", response_class=HTMLResponse)
async def home_disabled(request: Request):
    status_info = {
        "status": "ok",
        "source": "companiesInsights backend",
        "message": "The /home endpoint is temporarily disabled. Please use /dashboard instead.",
    }
    return render("status.html", request, status_info)