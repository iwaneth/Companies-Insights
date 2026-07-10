from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
import asyncio
from nocodb_client import fetch_table

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)

def clean_record(record: dict) -> dict:
    return {
        key: "" if isinstance(value, str) and value.strip().lower() in {"null", "none"} else value
        for key, value in record.items()
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def home(request: Request):
    profileData, newsData = await asyncio.gather(
        fetch_table("profile_and_news", "profile"),
        fetch_table("profile_and_news", "lastNews"),
    )
    profile_rows = [clean_record(company) for company in profileData.get("list", [])]
    news_rows = [clean_record(article) for article in newsData.get("list", [])]

    companies = []
    for company in profile_rows:
        company_news = [
            article
            for article in news_rows
            if article.get("companyName") == company.get("companyName")
        ]
        companies.append({**company, "news": company_news})

    return render(
        "dashboard.html",
        request,
        {
            "companies": companies,
            "news": news_rows,
        },
    )
