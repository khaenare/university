import os


class Config:
    HOST = os.getenv("APP_HOST", "127.0.0.1")
    PORT = int(os.getenv("APP_PORT", "8000"))
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/periodicals",
    )
    SECRET = os.getenv("APP_SECRET", "change-me-for-production")
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "views")
