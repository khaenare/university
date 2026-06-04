from app.dao.connection import Database
from app.models.payment import Payment


class PaymentDao:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(self, payment: Payment) -> int:
        sql = "INSERT INTO payments(subscription_id, amount, status) VALUES (%s, %s, %s) RETURNING id"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (payment.subscription_id, payment.amount, payment.status))
            return cur.fetchone()[0]

    def list_for_subscription(self, subscription_id: int) -> list[Payment]:
        sql = "SELECT id, subscription_id, amount, status FROM payments WHERE subscription_id=%s ORDER BY id DESC"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (subscription_id,))
            return [Payment(*row) for row in cur.fetchall()]

    def find_by_id(self, payment_id: int) -> Payment | None:
        sql = "SELECT id, subscription_id, amount, status FROM payments WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (payment_id,))
            row = cur.fetchone()
            return Payment(*row) if row else None

    def update_status(self, payment_id: int, status: str) -> None:
        sql = "UPDATE payments SET status=%s WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (status, payment_id))

    def delete(self, payment_id: int) -> None:
        sql = "DELETE FROM payments WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (payment_id,))
