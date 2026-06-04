import unittest
from decimal import InvalidOperation

from app.controllers.subscription_controller import SubscriptionController
from app.core.request import Request
from app.models.user import User


class FakeTemplates:
    def render(self, template_name, model):
        return f"{template_name}:{model.get('message', '')}"


class FakePublicationService:
    def list_publications(self):
        return []


class RaisingSubscriptionService:
    def __init__(self, exception):
        self.exception = exception

    def update_subscription(self, *args):
        raise self.exception

    def delete_subscription(self, *args):
        raise self.exception

    def register_payment(self, *args):
        raise self.exception


def request(body):
    result = Request("POST", "/subscriptions/update", {}, body)
    result.user = User(5, "reader", "", "reader")
    return result


class SubscriptionControllerErrorTest(unittest.TestCase):
    def test_update_returns_400_for_value_error(self):
        controller = SubscriptionController(
            FakeTemplates(),
            RaisingSubscriptionService(ValueError("Subscription not found")),
            FakePublicationService(),
        )

        response = controller.update(request("subscription_id=404&months=1"))

        self.assertEqual(400, response.status)
        self.assertIn("Subscription not found", response.body)

    def test_delete_returns_403_for_permission_error(self):
        controller = SubscriptionController(
            FakeTemplates(),
            RaisingSubscriptionService(PermissionError("forbidden")),
            FakePublicationService(),
        )

        response = controller.delete(request("subscription_id=7"))

        self.assertEqual(403, response.status)
        self.assertIn("Немає доступу", response.body)

    def test_create_payment_returns_400_for_invalid_decimal(self):
        controller = SubscriptionController(
            FakeTemplates(),
            RaisingSubscriptionService(InvalidOperation()),
            FakePublicationService(),
        )

        response = controller.create_payment(request("subscription_id=7&amount=bad"))

        self.assertEqual(400, response.status)
        self.assertIn("error.html", response.body)


if __name__ == "__main__":
    unittest.main()
