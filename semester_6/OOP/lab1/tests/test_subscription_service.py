import unittest
from decimal import Decimal

from app.models.publication import Publication
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscription_service import SubscriptionService


class FakePublicationDao:
    def find_by_id(self, publication_id):
        if publication_id == 10:
            return Publication(10, "Журнал", "Видавець", 1, Decimal("25.50"))
        return None


class FakeSubscriptionDao:
    def __init__(self):
        self.created = None

    def create(self, subscription: Subscription):
        self.created = subscription
        return 7

    def list_for_user(self, user_id):
        return []

    def find_by_id(self, subscription_id):
        return Subscription(subscription_id, 5, 10, 2, Decimal("51.00"), "created")

    def update(self, subscription):
        self.created = subscription

    def delete(self, subscription_id):
        self.deleted = subscription_id


class FakePaymentDao:
    def __init__(self):
        self.created = None

    def create(self, payment):
        self.created = payment
        return 3

    def list_for_subscription(self, subscription_id):
        return []

    def find_by_id(self, payment_id):
        return Payment(payment_id, 7, Decimal("51.00"), "registered")

    def update_status(self, payment_id, status):
        self.updated = (payment_id, status)

    def delete(self, payment_id):
        self.deleted = payment_id


class MissingSubscriptionDao(FakeSubscriptionDao):
    def find_by_id(self, subscription_id):
        return None


class MissingPaymentDao(FakePaymentDao):
    def find_by_id(self, payment_id):
        return None


class SubscriptionServiceTest(unittest.TestCase):
    def test_calculate_total(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), FakePaymentDao())

        self.assertEqual(Decimal("76.50"), service.calculate_total(10, 3))

    def test_subscribe_creates_subscription_with_total(self):
        subscription_dao = FakeSubscriptionDao()
        service = SubscriptionService(FakePublicationDao(), subscription_dao, FakePaymentDao())

        subscription_id = service.subscribe(5, 10, 2)

        self.assertEqual(7, subscription_id)
        self.assertEqual(Decimal("51.00"), subscription_dao.created.total_amount)
        self.assertEqual(5, subscription_dao.created.user_id)

    def test_register_payment(self):
        payment_dao = FakePaymentDao()
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), payment_dao)

        payment_id = service.register_payment(7, Decimal("51.00"), User(5, "reader", "", "reader"))

        self.assertEqual(3, payment_id)
        self.assertEqual(7, payment_dao.created.subscription_id)

    def test_register_payment_rejects_foreign_subscription(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), FakePaymentDao())

        with self.assertRaises(PermissionError):
            service.register_payment(7, Decimal("51.00"), User(9, "other", "", "reader"))

    def test_update_subscription_recalculates_total(self):
        subscription_dao = FakeSubscriptionDao()
        service = SubscriptionService(FakePublicationDao(), subscription_dao, FakePaymentDao())

        service.update_subscription(7, 4, User(5, "reader", "", "reader"))

        self.assertEqual(Decimal("102.00"), subscription_dao.created.total_amount)

    def test_payment_status_update_requires_access(self):
        payment_dao = FakePaymentDao()
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), payment_dao)

        service.update_payment_status(3, "paid", User(5, "reader", "", "reader"))

        self.assertEqual((3, "paid"), payment_dao.updated)

    def test_rejects_invalid_months(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), FakePaymentDao())

        with self.assertRaises(ValueError):
            service.subscribe(5, 10, 0)

    def test_rejects_missing_subscription_for_payment(self):
        service = SubscriptionService(FakePublicationDao(), MissingSubscriptionDao(), FakePaymentDao())

        with self.assertRaises(ValueError):
            service.register_payment(404, Decimal("10.00"), User(5, "reader", "", "reader"))

    def test_rejects_invalid_payment_amount(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), FakePaymentDao())

        with self.assertRaises(ValueError):
            service.register_payment(7, Decimal("0"), User(5, "reader", "", "reader"))

    def test_rejects_invalid_payment_status(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), FakePaymentDao())

        with self.assertRaises(ValueError):
            service.update_payment_status(3, "unknown", User(5, "reader", "", "reader"))

    def test_rejects_missing_payment(self):
        service = SubscriptionService(FakePublicationDao(), FakeSubscriptionDao(), MissingPaymentDao())

        with self.assertRaises(ValueError):
            service.delete_payment(404, User(5, "reader", "", "reader"))


if __name__ == "__main__":
    unittest.main()
