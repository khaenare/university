import logging
from decimal import Decimal

from app.models import Payment, Publication, Subscription, User
from app.repositories import PaymentRepository, PublicationRepository, SubscriptionRepository, UserRepository
from app.security import create_access_token, verify_password


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def authenticate(self, username: str, password: str) -> tuple[str, User] | None:
        user = self._users.find_by_username(username)
        if user and verify_password(password, user.password_hash):
            logging.info("User %s authenticated", username)
            return create_access_token(user.id, user.username, user.role), user
        logging.warning("Failed login for %s", username)
        return None


class PublicationService:
    def __init__(self, publications: PublicationRepository) -> None:
        self._publications = publications

    def list_publications(self) -> list[Publication]:
        return self._publications.list_all()

    def create(self, title: str, publisher: str, period_months: int, price: Decimal) -> Publication:
        publication = self._publications.create(Publication(title=title, publisher=publisher, period_months=period_months, price=price))
        logging.info("Publication %s created", publication.id)
        return publication

    def update(self, publication_id: int, title: str, publisher: str, period_months: int, price: Decimal) -> Publication:
        publication = self._require_publication(publication_id)
        publication.title = title
        publication.publisher = publisher
        publication.period_months = period_months
        publication.price = price
        logging.info("Publication %s updated", publication.id)
        return self._publications.update(publication)

    def delete(self, publication_id: int) -> None:
        publication = self._require_publication(publication_id)
        self._publications.delete(publication)
        logging.info("Publication %s deleted", publication_id)

    def _require_publication(self, publication_id: int) -> Publication:
        publication = self._publications.find_by_id(publication_id)
        if publication is None:
            raise ValueError("Publication not found")
        return publication


class SubscriptionService:
    ALLOWED_PAYMENT_STATUSES = {"registered", "paid", "cancelled"}

    def __init__(self, publications: PublicationRepository, subscriptions: SubscriptionRepository, payments: PaymentRepository) -> None:
        self._publications = publications
        self._subscriptions = subscriptions
        self._payments = payments

    def calculate_total(self, publication_id: int, months: int) -> Decimal:
        if months <= 0:
            raise ValueError("Months must be positive")
        publication = self._publications.find_by_id(publication_id)
        if publication is None:
            raise ValueError("Publication not found")
        return publication.price * Decimal(months)

    def list_for_user(self, user: User) -> list[Subscription]:
        return self._subscriptions.list_for_user(user)

    def subscribe(self, user: User, publication_id: int, months: int) -> Subscription:
        total = self.calculate_total(publication_id, months)
        subscription = self._subscriptions.create(Subscription(user_id=user.id, publication_id=publication_id, months=months, total_amount=total))
        logging.info("User %s created subscription %s", user.id, subscription.id)
        return subscription

    def update_subscription(self, subscription_id: int, months: int, user: User) -> Subscription:
        subscription = self._require_subscription_access(subscription_id, user)
        subscription.months = months
        subscription.total_amount = self.calculate_total(subscription.publication_id, months)
        logging.info("Subscription %s updated", subscription.id)
        return self._subscriptions.update(subscription)

    def delete_subscription(self, subscription_id: int, user: User) -> None:
        subscription = self._require_subscription_access(subscription_id, user)
        self._subscriptions.delete(subscription)
        logging.info("Subscription %s deleted", subscription_id)

    def register_payment(self, subscription_id: int, amount: Decimal, user: User) -> Payment:
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        self._require_subscription_access(subscription_id, user)
        payment = self._payments.create(Payment(subscription_id=subscription_id, amount=amount))
        logging.info("Payment %s registered", payment.id)
        return payment

    def list_payments(self, subscription_id: int, user: User) -> list[Payment]:
        self._require_subscription_access(subscription_id, user)
        return self._payments.list_for_subscription(subscription_id)

    def update_payment_status(self, payment_id: int, status: str, user: User) -> Payment:
        if status not in self.ALLOWED_PAYMENT_STATUSES:
            raise ValueError("Unsupported payment status")
        payment = self._require_payment_access(payment_id, user)
        payment.status = status
        logging.info("Payment %s status changed to %s", payment_id, status)
        return self._payments.update(payment)

    def delete_payment(self, payment_id: int, user: User) -> None:
        payment = self._require_payment_access(payment_id, user)
        self._payments.delete(payment)
        logging.info("Payment %s deleted", payment_id)

    def _require_subscription_access(self, subscription_id: int, user: User) -> Subscription:
        subscription = self._subscriptions.find_by_id(subscription_id)
        if subscription is None:
            raise ValueError("Subscription not found")
        if not user.is_admin and subscription.user_id != user.id:
            raise PermissionError("Subscription belongs to another user")
        return subscription

    def _require_payment_access(self, payment_id: int, user: User) -> Payment:
        payment = self._payments.find_by_id(payment_id)
        if payment is None:
            raise ValueError("Payment not found")
        self._require_subscription_access(payment.subscription_id, user)
        return payment
