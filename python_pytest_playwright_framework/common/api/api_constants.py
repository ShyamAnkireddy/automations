import os

DEFAULT_API_BASE_URL = os.getenv(
    "API_BASE_URL", "https://jsonplaceholder.typicode.com"
).rstrip("/")
DEFAULT_ALLOWED_HOSTS = tuple(
    host.strip().lower()
    for host in os.getenv(
        "API_ALLOWED_HOSTS", "jsonplaceholder.typicode.com"
    ).split(",")
    if host.strip()
)
DEFAULT_API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "10"))
