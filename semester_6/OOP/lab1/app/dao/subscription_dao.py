from app.dao.connection import Database
from app.models.subscription import Subscription


class SubscriptionDao:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(self, subscription: Subscription) -> int:
        sql = """
            INSERT INTO subscriptions(user_id, publication_id, months, total_amount, status)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (
                subscription.user_id,
                subscription.publication_id,
                subscription.months,
                subscription.total_amount,
                subscription.status,
            ))
            return cur.fetchone()[0]

    def list_for_user(self, user_id: int) -> list[Subscription]:
        sql = "SELECT id, user_id, publication_id, months, total_amount, status FROM subscriptions WHERE user_id=%s ORDER BY id DESC"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            return [Subscription(*row) for row in cur.fetchall()]

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        sql = "SELECT id, user_id, publication_id, months, total_amount, status FROM subscriptions WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (subscription_id,))
            row = cur.fetchone()
            return Subscription(*row) if row else None

    def update(self, subscription: Subscription) -> None:
        sql = "UPDATE subscriptions SET months=%s, total_amount=%s, status=%s WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (subscription.months, subscription.total_amount, subscription.status, subscription.id))

    def delete(self, subscription_id: int) -> None:
        sql = "DELETE FROM subscriptions WHERE id=%s"
        with self._db.connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (subscription_id,))
