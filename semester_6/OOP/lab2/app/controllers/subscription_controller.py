from decimal import Decimal
from decimal import InvalidOperation

from app.core.controller import Controller


class SubscriptionController(Controller):
    def __init__(self, templates, subscription_service, publication_service) -> None:
        super().__init__(templates)
        self._subscription_service = subscription_service
        self._publication_service = publication_service

    def index(self, request):
        return self.render("subscriptions.html", {
            "user": request.user,
            "subscriptions": self._subscription_service.list_for_user(request.user.id),
            "publications": self._publication_service.list_publications(),
        })

    def create(self, request):
        try:
            self._subscription_service.subscribe(
                request.user.id,
                int(request.param("publication_id")),
                int(request.param("months")),
            )
        except ValueError as error:
            return self._error(request, str(error), 400)
        return self.redirect("/subscriptions")

    def update(self, request):
        try:
            self._subscription_service.update_subscription(
                int(request.param("subscription_id")),
                int(request.param("months")),
                request.user,
            )
        except PermissionError:
            return self._error(request, "Немає доступу до цієї передплати", 403)
        except ValueError as error:
            return self._error(request, str(error), 400)
        return self.redirect("/subscriptions")

    def delete(self, request):
        try:
            self._subscription_service.delete_subscription(int(request.param("subscription_id")), request.user)
        except PermissionError:
            return self._error(request, "Немає доступу до цієї передплати", 403)
        except ValueError as error:
            return self._error(request, str(error), 400)
        return self.redirect("/subscriptions")

    def payment_page(self, request):
        payments = []
        subscription_id = request.param("subscription_id")
        if subscription_id:
            try:
                payments = self._subscription_service.list_payments(int(subscription_id), request.user)
            except PermissionError:
                return self._error(request, "Немає доступу до платежів", 403)
            except ValueError as error:
                return self._error(request, str(error), 400)
        return self.render("payment.html", {"user": request.user, "payments": payments, "subscription_id": subscription_id})

    def create_payment(self, request):
        try:
            self._subscription_service.register_payment(
                int(request.param("subscription_id")),
                Decimal(request.param("amount")),
                request.user,
            )
        except PermissionError:
            return self._error(request, "Немає доступу до цієї передплати", 403)
        except (ValueError, InvalidOperation) as error:
            return self._error(request, str(error), 400)
        return self.redirect("/subscriptions")

    def update_payment(self, request):
        try:
            self._subscription_service.update_payment_status(
                int(request.param("payment_id")),
                request.param("status"),
                request.user,
            )
        except PermissionError:
            return self._error(request, "Немає доступу до платежу", 403)
        except ValueError as error:
            return self._error(request, str(error), 400)
        return self.redirect("/payment")

    def delete_payment(self, request):
        try:
            self._subscription_service.delete_payment(int(request.param("payment_id")), request.user)
        except PermissionError:
            return self._error(request, "Немає доступу до платежу", 403)
        except ValueError as error:
            return self._error(request, str(error), 400)
        return self.redirect("/payment")

    def _error(self, request, message: str, status: int):
        return self.render("error.html", {"user": request.user, "message": message}, status)
