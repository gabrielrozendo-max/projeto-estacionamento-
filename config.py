import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    XANO_BASE_URL = os.getenv("XANO_BASE_URL", "").strip().rstrip("/")
    XANO_API_KEY = os.getenv("XANO_API_KEY", "").strip()
    XANO_TIMEOUT_SECONDS = float(os.getenv("XANO_TIMEOUT_SECONDS", "5"))