FROM python:3.14.10-slim-trixie

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]  

# note: The CMD command is set to run the FastAPI application using uvicorn.
# It navigates to the /app/backend directory and starts the server on all available network interfaces (0.0.0.0) on port 8000
# note: (0.0.0.0) and (8000) are only chosen for the simplicity in development and testing.