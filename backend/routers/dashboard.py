from pathlib import Path
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db_client import fetch_table

def _as_datetime(value):
    if isinstance(value, datetime):
        return value
    if not value or not isinstance(value, str):
        return None
    cleaned = value.replace("Z", "+00:00").strip()
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        try:
            return datetime.strptime(cleaned[:10], "%Y-%m-%d")
        except ValueError:
            return None


def format_date(value):
    dt = _as_datetime(value)
    if dt is None:
        return "" if not isinstance(value, str) else value
    if dt.tzinfo is None:
        delta = datetime.now() - dt
    else:
        delta = datetime.now(dt.tzinfo) - dt
    days = delta.days
    if days < 0:
        return value if isinstance(value, str) else dt.date().isoformat()
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days} days ago"
    if days < 30:
        return f"{days // 7} weeks ago"
    if days < 365:
        return f"{days // 30} months ago"
    return f"{days // 365} years ago"


def pubdate_fmt(value):
    """Format a date to dd/mm/yy."""
    dt = _as_datetime(value)
    if dt is None:
        return "" if not isinstance(value, str) else value
    return f"{dt.day:02d}/{dt.month:02d}/{str(dt.year)[-2:]}"
    
router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))
templates.env.filters["pubdate_fmt"] = pubdate_fmt
templates.env.filters["format_date"] = format_date

def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    return templates.TemplateResponse(request=request, name=template_name, context=context)

def clean_record(record: dict) -> dict:
    return {
        key: "" if isinstance(value, str) and value.strip().lower() in {"null", "none"} else value
        for key, value in record.items()
    }

COMPANY_DETAIL_FIELDS = (
    "founded",
    "website",
    "headquarters",
    "country",
    "stockSymbole",
    "stockExchange",
    "parentCompany",
    "subsidiaries",
)
PROPERTY_FIELDS = (
    "revenue",
    "employees",
    "keyProducts",
    "ceo",
    "netIncome",
    "marketCap",
)
PROFILE_FIELDS = ("profile", "competitors", "tags")
NEWS_FIELDS = ("title", "pubDate", "newsArticle")

FIELD_LABELS = {
    "companyName": "Company Name",
    "industry": "Industry",
    "founded": "Founded",
    "website": "Website",
    "headquarters": "Headquarters",
    "stockSymbole": "Stock Symbol",
    "country": "Country",
    "stockExchange": "Stock Exchange",
    "parentCompany": "Parent Company",
    "subsidiaries": "Subsidiaries",
    "revenue": "Revenue",
    "employees": "Employees",
    "keyProducts": "Key Products",
    "ceo": "CEO",
    "netIncome": "Net Income",
    "marketCap": "Market Cap",
    "profile": "Profile",
    "competitors": "Competitors",
    "tags": "Tags",
    "title": "Title",
    "pubDate": "Published",
    "newsArticle": "Article",
}

def humanize_field(key=None):
    """Convert snake_case to Title Case or use mapping."""
    if not key or not isinstance(key, str):
        return ""
    return FIELD_LABELS.get(key, key.replace("_", " ").title())


def present_fields(record: dict, fields: tuple[str, ...]) -> dict:
    presented = {}
    for key in fields:
        value = record.get(key)
        if value in (None, "", []):
            continue
        presented[key] = value
    return presented

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
                "id": company_id,
                "companyName": company.get("companyName") or "",
                "industry": company.get("industry") or "",
                "details": present_fields(company, COMPANY_DETAIL_FIELDS),
                "profiles": [
                    present_fields(row, PROFILE_FIELDS)
                    for row in profiles_by_company.get(company_id, [])
                ],
                "properties": [
                    present_fields(row, PROPERTY_FIELDS)
                    for row in properties_by_company.get(company_id, [])
                ],
                "news": [
                    present_fields(row, NEWS_FIELDS)
                    for row in news_by_company.get(company_id, [])
                ],
            }
        )

    return render(
    "dashboard.html",
    request,
    {
        "companies": companies,
        "humanize_field": humanize_field,
        "format_date": format_date,
        "pubdate_fmt": pubdate_fmt,
    }
)
