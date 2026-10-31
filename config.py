import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

class Config:
    XANO_BASE_URL = (
        os.getenv("XANO_BASE_URL")
        or "https://x8ki-letl-twmt.n7.xano.io/api:_9r2HLxO"
    ).strip().rstrip("/")
    XANO_TIMEOUT_SECONDS = float(os.getenv("XANO_TIMEOUT_SECONDS", "5"))