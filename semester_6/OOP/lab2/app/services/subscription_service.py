from decimal import Decimal

from app.models.payment import Payment
from app.models.subscription import Subscription


class SubscriptionService:
    ALLOWED_PAYMENT_STATUSES = {"registered", "paid", "cancelled"}

    def __init__(self, publication_dao, subscription_dao, payment_dao) -> None:
        self._publication_dao = publication_dao
        self._subscription_dao = subscription_dao
        self._payment_dao = payment_dao

    def calculate_total(self, publication_id: int, months: int) -> Decimal:
        if months <= 0:
            raise ValueError("Months must be positive")
        publication = self._publication_dao.find_by_id(publication_id)
        if publication is None:
            raise ValueError("Publication not found")
        return publication.price * Decimal(months)

    def subscribe(self, user_id: int, publication_id: int, months: int) -> int:
        total = self.calculate_total(publication_id, months)
        subscription = Subscription(None, user_id, publication_id, months, total)
        return self._subscription_dao.create(subscription)

    def _require_subscription_access(self, subscription_id: int, user) -> Subscription:
        subscription = self._subscription_dao.find_by_id(subscription_id)
        if subscription is None:
            raise ValueError("Subscription not found")
        if not user.is_admin and subscription.user_id != user.id:
            raise PermissionError("Subscription belongs to another user")
        return subscription

    def update_subscription(self, subscription_id: int, months: int, user) -> None:
        subscription = self._require_subscription_access(subscription_id, user)
        total = self.calculate_total(subscription.publication_id, months)
        self._subscription_dao.update(Subscription(
            subscription.id,
            subscription.user_id,
            subscription.publication_id,
            months,
            total,
            subscription.status,
        ))

    def delete_subscription(self, subscription_id: int, user) -> None:
        self._require_subscription_access(subscription_id, user)
        self._subscription_dao.delete(subscription_id)

    def register_payment(self, subscription_id: int, amount: Decimal, user) -> int:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        self._require_subscription_access(subscription_id, user)
        return self._payment_dao.create(Payment(None, subscription_id, amount))

    def list_payments(self, subscription_id: int, user):
        self._require_subscription_access(subscription_id, user)
        return self._payment_dao.list_for_subscription(subscription_id)

    def _require_payment_access(self, payment_id: int, user) -> Payment:
        payment = self._payment_dao.find_by_id(payment_id)
        if payment is None:
            raise ValueError("Payment not found")
        self._require_subscription_access(payment.subscription_id, user)
        return payment

    def update_payment_status(self, payment_id: int, status: str, user) -> None:
        if status not in self.ALLOWED_PAYMENT_STATUSES:
            raise ValueError("Unsupported payment status")
        self._require_payment_access(payment_id, user)
        self._payment_dao.update_status(payment_id, status)

    def delete_payment(self, payment_id: int, user) -> None:
        self._require_payment_access(payment_id, user)
        self._payment_dao.delete(payment_id)

    def list_for_user(self, user_id: int):
        return self._subscription_dao.list_for_user(user_id)
