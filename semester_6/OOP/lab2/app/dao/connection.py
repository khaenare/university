import psycopg

from app.config import Config


class Database:
    def __init__(self, dsn: str = Config.DATABASE_URL) -> None:
        self._dsn = dsn

    def connect(self):
        return psycopg.connect(self._dsn)
