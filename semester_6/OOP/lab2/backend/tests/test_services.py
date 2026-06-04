from decimal import Decimal

import pytest

from app.models import Payment, Publication, Subscription, User
from app.security import hash_password, verify_password
from app.services import AuthService, SubscriptionService


class FakeUsers:
    def __init__(self, user=None):
        self.user = user

    def find_by_username(self, username):
        return self.user if self.user and self.user.username == username else None


class FakePublications:
    def find_by_id(self, publication_id):
        if publication_id == 10:
            return Publication(id=10, title="Журнал", publisher="Видавець", period_months=1, price=Decimal("25.50"))
        return None


class FakeSubscriptions:
    def __init__(self):
        self.saved = None

    def create(self, subscription):
        subscription.id = 7
        subscription.publication = Publication(id=10, title="Журнал", publisher="Видавець", period_months=1, price=Decimal("25.50"))
        self.saved = subscription
        return subscription

    def list_for_user(self, user):
        return []

    def find_by_id(self, subscription_id):
        return Subscription(id=subscription_id, user_id=5, publication_id=10, months=2, total_amount=Decimal("51.00"), status="created")

    def update(self, subscription):
        self.saved = subscription
        return subscription

    def delete(self, subscription):
        self.deleted = subscription.id


class FakePayments:
    def __init__(self):
        self.saved = None

    def create(self, payment):
        payment.id = 3
        self.saved = payment
        return payment

    def list_for_subscription(self, subscription_id):
        return []

    def find_by_id(self, payment_id):
        return Payment(id=payment_id, subscription_id=7, amount=Decimal("51.00"), status="registered")

    def update(self, payment):
        self.saved = payment
        return payment

    def delete(self, payment):
        self.deleted = payment.id


def test_password_hash_verification():
    password_hash = hash_password("password")

    assert verify_password("password", password_hash)
    assert not verify_password("wrong", password_hash)


def test_authenticate_returns_jwt_and_user():
    user = User(id=1, username="reader", password_hash=hash_password("password"), role="reader")
    result = AuthService(FakeUsers(user)).authenticate("reader", "password")

    assert result is not None
    token, authenticated = result
    assert token
    assert authenticated.username == "reader"


def test_calculate_total():
    service = SubscriptionService(FakePublications(), FakeSubscriptions(), FakePayments())

    assert service.calculate_total(10, 3) == Decimal("76.50")


def test_subscribe_creates_subscription_with_total():
    subscriptions = FakeSubscriptions()
    service = SubscriptionService(FakePublications(), subscriptions, FakePayments())

    subscription = service.subscribe(User(id=5, username="reader", password_hash="", role="reader"), 10, 2)

    assert subscription.id == 7
    assert subscriptions.saved.total_amount == Decimal("51.00")
    assert subscriptions.saved.user_id == 5


def test_register_payment_rejects_foreign_subscription():
    service = SubscriptionService(FakePublications(), FakeSubscriptions(), FakePayments())

    with pytest.raises(PermissionError):
        service.register_payment(7, Decimal("51.00"), User(id=9, username="other", password_hash="", role="reader"))


def test_update_payment_rejects_invalid_status():
    service = SubscriptionService(FakePublications(), FakeSubscriptions(), FakePayments())
    with pytest.raises(ValueError):
        service.update_payment_status(3, "unknown", User(id=5, username="reader", password_hash="", role="reader"))
