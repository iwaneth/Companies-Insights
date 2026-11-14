# Companies Insights

![Docker](https://img.shields.io/badge/docker-required-2496ED)

![n8n](https://img.shields.io/badge/n8n-automation-EA4B73)

![Supabase](https://img.shields.io/badge/Supabase-backend%20database-3ECF8E)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688)

A containerized full-stack enterprise intelligence platform that automatically collects, analyzes, and aggregates company profile and news data. Built with **Docker**, **n8n** for workflow automation, **Supabase** for data storage, and a **FastAPI + Jinja2** dashboard.

## Overview

Company Intelligence monitors companies and aggregates everything known about them into interactive dashboard cards:

- **News Fetching**: n8n workflows continuously collect the latest news for tracked companies
- **Constant and Dynamic Attributes/Properties**: n8n workflows that fetches deep information and refreshes when informations change
- **Profile Fetching**: generates a profile from data provided (profile, competitores, tags)
- **Dashboard**: a FastAPI-rendered page groups profiles, constant and dynamic properties, and news into one card per company, with search, light/dark themes, hover article previews, and a details modal

With robust error handling, multi-model AI fallback support, and containerized deployment, the platform runs anywhere Docker is available.

## Key Features

- **Automated Workflows**: n8n-powered pipelines for continuous data collection (definitions in `n8n-workflows/`)
- **Multi-AI Model Support**: built-in fallback nodes for multiple AI model API keys
- **Company Dashboard**: one card per company with news previews, client-side search, and a floating details modal
- **Light / Dark Themes**: VS Code-style dark theme, persisted across pages
- **Robust Error Handling**: error logging and tracking from the automation layer
- **Docker Containerized**: run the automation stack with a single `docker-compose` command
- **Secure Backend**: Supabase tables are private; FastAPI fetches data server-side only

### Data Collected

**Constant records** (`companies` table):

- Company name, industry
- Founded, website, headquarters, country
- Stock symbol / exchange, parent company, subsidiaries

**Dynamic properties** (`halfDynamicProperties` table):

- Revenue, employees, key products, CEO, net income, market cap

**Profiles** (`companyProfile` table):

- Profile text, competitors, tags

**News** (`companyNews` table):

- Article title, publication date, full article text

## Quick Start

### Prerequisites

- **Docker & Docker Compose** — [Install Docker](https://docs.docker.com/get-docker/) (for the n8n automation stack)
- **Python 3.10+** — [Install from python.org](https://www.python.org/downloads/) (to run the FastAPI backend locally)
- API Keys for AI models (OpenAI, Gemini, Groq, etc.) — used by the n8n workflows
- A Supabase project URL and secret key for the dashboard

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/iwaneth/CompanyIntelligence.git
   cd CompaniesInsights
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

3. **Configure `.env`**:

   The secret key is only for the FastAPI backend. Never put it in frontend code or expose it to browsers.

4. **Start the automation stack**:

   ```bash
   docker-compose up -d
   ```

5. **Access the services**:
   - **n8n Workflows**: http://localhost:5678
   - **Dashboard**: http://127.0.0.1:8000/dashboard (after starting the backend, see below)

### Post-Setup Configuration

#### Configure n8n Workflows

1. Access n8n at `http://localhost:5678`
2. Import the workflow definitions from `n8n-workflows/`:
   - `companyNews.json` — news collection
   - `companyProfile.json` — profile data refresh
   - `companies.json`, `companyH.json`, `addNewCompany.json`, `backToPending.json` — company management
   - `scheduleRefresher.json` — scheduled refresh / cleanup
3. In each workflow, configure the AI model nodes with your API keys and set up the required credentials (AI providers, Supabase, Discord webhook — optional)

#### Database Setup (Supabase)

Before using the dashboard, run `supabase/migrations/20261026221500_private_backend_company_data.sql` in the Supabase SQL Editor. It enables Row Level Security on the four company tables, revokes direct table access from `public`, `anon`, and `authenticated`, and grants table reads to the backend's `service_role`. The SQL files in `test-db/` are example seed statements and must be run separately if those sample rows have not already been imported.

The dashboard reads `companies`, `halfDynamicProperties`, `companyProfile`, and `companyNews`, joining child rows to company cards by `company_id`.

#### Back-end Starter

The backend can be started either by disabling the ["dev"] flag in profiles in docker-compose.yml, so docker compose starts it with the n8n container and handle all dependencies and virtual envirnment in the background, Or it can be started individually for devlopment purposes following these steps:

The Python interpreter selected on your computer is separate from the Python 3.12 runtime in Docker. To run the backend locally, create a project virtual environment and install dependencies once:

In the project directory, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1`.

Create `.env` from `.env.example` and set your Supabase project URL and a server-only Supabase secret key. Keep it private: do not commit `.env`, add the key to frontend code, or expose it to browsers. If `.env` currently contains `SUPABASE_KEY`, replace that variable with `SUPABASE_SECRET_KEY` using the secret key from Supabase's API settings.

Run the API from the repository root:

```bash
python -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000/dashboard. The website is public; FastAPI fetches the data server-side. This protects the Supabase tables from direct anonymous Supabase API queries, but data displayed on a public page can still be viewed and copied by visitors.( THIS steps uf u kept the `app` service in `docker-compose.yml` is disabled via a profile).

Run the backend tests without Docker:

```bash
PYTHONPATH=backend python -m pytest backend/
```

> **Note:** earlier versions of this project used NocoDB as the database and an `app.py`/`nocodb_client.py` backend. Those have been replaced by the Supabase + FastAPI dashboard described above.

## Project Structure

```
companiesInsights/
├── backend/
│   ├── main.py                  # FastAPI app, mounts static/scripts, routers
│   ├── config.py                # backend configuration
│   ├── db_client.py             # Supabase fetch client
│   ├── routers/
│   │   ├── dashboard.py         # /dashboard — groups tables into company cards
│   │   ├── home.py              # /home — currently a "temporarily disabled" page
│   │   └── features.py          # /features — settings placeholder
│   ├── test_app.py
│   └── test_db_client.py
├── frontend/
│   ├── templates/
│   │   ├── dashboard.html       # company cards, theme switcher, modals
│   │   ├── home.html
│   │   ├── features.html
│   │   └── status.html
│   ├── static/
│   │   ├── theme.css            # shared light/dark palette (edit dark colors here)
│   │   ├── dashboard.css
│   │   ├── home.css
│   │   ├── features.css
│   │   └── status.css
│   └── scripts/
│       ├── theme.js             # applies saved theme before first paint
│       └── dashboard.js         # search, theme switcher, news/company modals
├── n8n-workflows/               # n8n workflow definitions (JSON)
├── n8n_data/                    # n8n runtime data (git-ignored)
├── supabase/
│   └── migrations/              # RLS migration for the four company tables
├── test-db/                     # example seed SQL (git-ignored)
├── docker-compose.yml           # n8n service (+ optional app profile)
├── Dockerfile
├── docker-starter.sh
├── docker-stop.sh
├── requirements.txt
├── .env.example
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
└── tree.txt
```

## Configuration Details

### Dashboard

- **Theme**: light/dark toggle on the dashboard; choice is persisted in `localStorage` and shared by all pages. Dark palette lives in `frontend/static/theme.css` under `html.dark-theme`.
- **Search**: client-side filter over each card's `data-search` attribute (company name, industry, news titles).
- **Cards**: news snippets are clamped; hovering a news item shows the full article + publish date in an overlay; clicking a card opens a modal with all attributes, properties, profiles, and news.

### AI Model Fallback System

The n8n workflows support multiple AI model APIs with automatic fallback. If the primary model fails, fallback models keep the pipelines running.

### Error Handling & Logging

Workflow errors are logged for review (CSV error reports / n8n execution logs). Monitor these to identify patterns and improve workflows.

## Data Flow

```
Companies List (Supabase)
    ↓
n8n Workflows (News & Profile & Constant & Dynamic)
    ↓
AI Models (with fallbacks) / Web Scrapping (with error handling)
    ↓
Data Processing & Validation
    ↓
Supabase Database (RLS-protected)
    ↓
FastAPI Backend (server-side fetch)
    ↓
Frontend Dashboard (Jinja2 + CSS/JS)
```

## Troubleshooting

### Workflows not running?

- Check n8n container logs: `docker logs n8n_local`
- Verify all API keys are correctly configured
- Ensure required credentials exist in n8n

### Dashboard shows no data?

- Confirm `.env` has `SUPABASE_URL` and `SUPABASE_SECRET_KEY`
- Confirm the RLS migration has been applied in Supabase
- Check the backend logs for Supabase fetch errors
- The dashboard fetches up to 100 rows per table

### AI Model failures?

- Check API key validity for all configured models
- Monitor error logs from the workflows
- Verify fallback nodes are properly configured with alternative API keys

### Docker issues?

- Pull latest images: `docker-compose pull`
- Rebuild containers: `docker-compose up -d --build`
- Check Docker disk space: `docker system df`

## Roadmap

### Phase 1 (Done)

- ✅ n8n workflow orchestration
- ✅ Multi-model AI support with fallbacks
- ✅ Database integration
- ✅ Error handling & logging

### Phase 2 (Done)

- ✅ FastAPI backend
  - Server-side Supabase access with RLS-protected tables
  - Jinja2-rendered dashboard

### Phase 3 (Done)

- ✅ Frontend dashboard
  - Company cards with grouped news, attributes, and profiles
  - Client-side search, light/dark themes, details modal

### Phase 4 (Future - v2)

- Multi-user system
- User authentication & authorization
- Personalized dashboards
- Email notifications
- Custom alerts & filters

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Dependencies

- **Docker & Docker Compose**: containerization (n8n)
- **n8n**: workflow automation platform
- **Supabase**: hosted Postgres database with RLS
- **FastAPI**: modern Python web framework (backend)
- **Jinja2**: server-side templating
- **Multiple AI APIs**: OpenAI, Anthropic, Groq, Gemini, etc.

## Support

For issues, questions, or suggestions:

- Check the troubleshooting section above
- Review error logs from the workflows
- Check n8n and Supabase documentation

---

**Started in 28/05/2026 and still goes in rate of 4 hours a day**

**NOTE: STILL under development, some features needs further optimizations and cleaning especially n8n workflows.**

Last Updated: November 2026
