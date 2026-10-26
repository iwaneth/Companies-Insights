from pathlib import Path
import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db_client import fetch_table

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

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
    table_names = (
        "companies",
        "halfDynamicProperties",
        "companyProfile",
        "companyNews",
    )
    table_results = await asyncio.gather(
        *(fetch_table(table_name) for table_name in table_names)
    )
    rows_by_table = {
        table_name: [clean_record(row) for row in result.get("list", [])]
        for table_name, result in zip(table_names, table_results)
    }
    profiles_by_company: dict[object, list[dict]] = {}
    properties_by_company: dict[object, list[dict]] = {}
    news_by_company: dict[object, list[dict]] = {}

    for row in rows_by_table["companyProfile"]:
        profiles_by_company.setdefault(row.get("company_id"), []).append(row)
    for row in rows_by_table["halfDynamicProperties"]:
        properties_by_company.setdefault(row.get("company_id"), []).append(row)
    for row in rows_by_table["companyNews"]:
        news_by_company.setdefault(row.get("company_id"), []).append(row)

    companies = []
    for company in rows_by_table["companies"]:
        company_id = company.get("id")
        companies.append(
            {
                **company,
                "profiles": profiles_by_company.get(company_id, []),
                "properties": properties_by_company.get(company_id, []),
                "news": news_by_company.get(company_id, []),
            }
        )

    return render(
        "dashboard.html",
        request,
        {
            "companies": companies,
        },
    )
