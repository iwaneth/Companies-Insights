from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)


@router.get("/features", response_class=HTMLResponse)
async def features(request: Request):
    return render("features.html",request)
