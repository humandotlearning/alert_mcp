import os
from dotenv import load_dotenv

load_dotenv()

ALERT_API_BASE_URL = os.getenv("ALERT_API_BASE_URL", "http://localhost:8000")
