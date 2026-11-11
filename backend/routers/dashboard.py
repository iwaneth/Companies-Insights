from pathlib import Path
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db_client import fetch_table

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

def format_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return ""
    try:
        cleaned = date_str.replace('Z', '+00:00').strip()
        try:
            dt = datetime.fromisoformat(cleaned)
        except ValueError:
            dt = datetime.strptime(cleaned[:10], "%Y-%m-%d")
        if dt.tzinfo is None:
            delta = datetime.now() - dt
        else:
            delta = datetime.now(dt.tzinfo) - dt
        days = delta.days
        if days < 0:
            return date_str
        elif days == 0:
            return "today"
        elif days == 1:
            return "yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            return f"{days // 7} weeks ago"
        elif days < 365:
            return f"{days // 30} months ago"
        else:
            return f"{days // 365} years ago"
    except Exception:
        return date_str

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)

def clean_record(record: dict) -> dict:
    return {
        key: "" if isinstance(value, str) and value.strip().lower() in {"null", "none"} else value
        for key, value in record.items()
    }

FIELD_LABELS = {
    'companyName': 'Company Name',
    'industry': 'Industry',
    'founded': 'Founded',
    'website': 'Website',
    'status': 'Status',
    'lastCompanyUpdate': 'Last Updated',
    'headquarters': 'Headquarters',
    'stockSymbol': 'Stock Symbol',
    'wikidataId': 'Wikidata ID',
    'country': 'Country',
    'stockExchange': 'Stock Exchange',
}

def humanize_field(key=None):
    """Convert snake_case to Title Case or use mapping."""
    if not key or not isinstance(key, str):
        return ""
    return FIELD_LABELS.get(key, key.replace('_', ' ').title())

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
        "field_labels": FIELD_LABELS,
        "humanize_field": humanize_field,
         "format_date": format_date,
    }
)
