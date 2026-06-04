from decimal import Decimal

from app.dao.connection import Database
from app.models.publication import Publication


class PublicationDao:
    def __init__(self, db: Database) -> None:
        self._db = db

    def list_all(self) -> list[Publication]:
        sql = "SELECT id, title, publisher, period_months, price FROM publications ORDER BY title"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql)
            return [Publication(*row) for row in cur.fetchall()]

    def find_by_id(self, publication_id: int) -> Publication | None:
        sql = "SELECT id, title, publisher, period_months, price FROM publications WHERE id = %s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (publication_id,))
            row = cur.fetchone()
            return Publication(*row) if row else None

    def create(self, publication: Publication) -> int:
        sql = """
            INSERT INTO publications(title, publisher, period_months, price)
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (publication.title, publication.publisher, publication.period_months, publication.price))
            return cur.fetchone()[0]

    def update(self, publication: Publication) -> None:
        sql = "UPDATE publications SET title=%s, publisher=%s, period_months=%s, price=%s WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (publication.title, publication.publisher, publication.period_months, publication.price, publication.id))

    def delete(self, publication_id: int) -> None:
        sql = "DELETE FROM publications WHERE id = %s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (publication_id,))
