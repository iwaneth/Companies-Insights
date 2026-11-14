# Contributing to Companies Insightes

Contributions are welcome! Whether you have ideas for improvements, bug fixes, or want to help with the FastAPI backend, the n8n workflows, or frontend development, feel free to reach out.

### Areas for Contribution

- Improving workflow efficiency and adding new data sources
- Enhancing error handling and logging
- Backend development (FastAPI routers, Supabase queries in `backend/`)
- Frontend development (templates in `frontend/templates/`, styles in `frontend/static/`, scripts in `frontend/scripts/`)
- n8n workflow improvements (definitions in `n8n-workflows/`)
- Design suggestions (the theme palette lives in `frontend/static/theme.css`)
- Testing and quality assurance

### Running the project locally

```bash
# Backend (from repo root, with .venv activated)
python -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000

# Tests
PYTHONPATH=backend python -m pytest backend/

# Automation stack
docker-compose up -d   # n8n on http://localhost:5678
                       # AND IF Dockerfile app was enabled in docker-compose.yml it will be accessible at: http://localhost:8000
```

### Conventions

- Secrets live only in `.env` / n8n credentials — never commit them (see `SECURITY.md`)
- The Supabase secret key is server-side only; never expose it to frontend code
- Theme colors are CSS variables in `frontend/static/theme.css` — reuse them instead of hardcoding colors
