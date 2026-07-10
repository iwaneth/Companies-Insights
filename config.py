import os
from dotenv import load_dotenv

load_dotenv()

NOCODB_BASE = os.getenv("NOCODB_BASE_URL")
NOCODB_API_KEY = os.getenv("NOCODB_API_KEY")
NOCODB_SQLITE_PATH = os.getenv("NOCODB_SQLITE_PATH")
NOCODB_TIMEOUT_SECONDS = float(os.getenv("NOCODB_TIMEOUT_SECONDS", "6.0"))