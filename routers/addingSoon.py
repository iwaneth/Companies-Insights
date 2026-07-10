from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)


@router.get("/features", response_class=HTMLResponse)
async def features(request: Request):
    return render("addingSoon.html",request)
