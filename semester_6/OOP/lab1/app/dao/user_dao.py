from app.dao.connection import Database
from app.models.user import User


class UserDao:
    def __init__(self, db: Database) -> None:
        self._db = db

    def find_by_username(self, username: str) -> User | None:
        sql = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (username,))
            row = cur.fetchone()
            return User(*row) if row else None

    def find_by_id(self, user_id: int) -> User | None:
        sql = "SELECT id, username, password_hash, role FROM users WHERE id = %s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            row = cur.fetchone()
            return User(*row) if row else None
