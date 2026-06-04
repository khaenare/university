import logging
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.config import Config
from app.commands.base import ControllerCommand
from app.controllers.auth_controller import AuthController
from app.controllers.publication_controller import PublicationController
from app.controllers.subscription_controller import SubscriptionController
from app.core.request import Request
from app.core.response import Response
from app.core.router import Router
from app.core.session import SessionStore
from app.core.template_engine import TemplateEngine
from app.dao.connection import Database
from app.dao.payment_dao import PaymentDao
from app.dao.publication_dao import PublicationDao
from app.dao.subscription_dao import SubscriptionDao
from app.dao.user_dao import UserDao
from app.services.auth_service import AuthService
from app.services.publication_service import PublicationService
from app.services.subscription_service import SubscriptionService


class Application:
    def __init__(self) -> None:
        templates = TemplateEngine(Config.TEMPLATE_DIR)
        db = Database()
        self.sessions = SessionStore()
        self.users = UserDao(db)
        publication_dao = PublicationDao(db)
        publication_service = PublicationService(publication_dao)
        subscription_service = SubscriptionService(publication_dao, SubscriptionDao(db), PaymentDao(db))
        auth = AuthController(templates, AuthService(self.users), self.sessions)
        publications = PublicationController(templates, publication_service)
        subscriptions = SubscriptionController(templates, subscription_service, publication_service)
        self.router = Router()
        self.router.add("GET", "/login", ControllerCommand(auth.login_page), auth_required=False)
        self.router.add("POST", "/login", ControllerCommand(auth.login), auth_required=False)
        self.router.add("GET", "/logout", ControllerCommand(auth.logout))
        self.router.add("GET", "/publications", ControllerCommand(publications.index))
        self.router.add("GET", "/publications/new", ControllerCommand(publications.new))
        self.router.add("POST", "/publications/create", ControllerCommand(publications.create))
        self.router.add("POST", "/publications/update", ControllerCommand(publications.update))
        self.router.add("POST", "/publications/delete", ControllerCommand(publications.delete))
        self.router.add("GET", "/subscriptions", ControllerCommand(subscriptions.index))
        self.router.add("POST", "/subscriptions/create", ControllerCommand(subscriptions.create))
        self.router.add("POST", "/subscriptions/update", ControllerCommand(subscriptions.update))
        self.router.add("POST", "/subscriptions/delete", ControllerCommand(subscriptions.delete))
        self.router.add("GET", "/payment", ControllerCommand(subscriptions.payment_page))
        self.router.add("POST", "/payment/create", ControllerCommand(subscriptions.create_payment))
        self.router.add("POST", "/payment/update", ControllerCommand(subscriptions.update_payment))
        self.router.add("POST", "/payment/delete", ControllerCommand(subscriptions.delete_payment))

    def handle(self, request: Request) -> Response:
        if request.path.startswith("/static/"):
            return self._static_response(request.path)
        route = self.router.resolve(request.method, request.path)
        if route is None:
            return Response.not_found()
        if route.auth_required:
            cookie = request.cookies.get("SESSION_ID")
            user_id = self.sessions.get_user_id(cookie.value if cookie else None)
            request.user = self.users.find_by_id(user_id) if user_id else None
            if request.user is None:
                return Response.redirect("/login")
        return route.command.process(request)

    def _static_response(self, url_path: str) -> Response:
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        requested = os.path.normpath(os.path.join(static_dir, url_path.removeprefix("/static/")))
        if os.path.commonpath([static_dir, requested]) != static_dir or not os.path.isfile(requested):
            return Response.not_found()
        with open(requested, "r", encoding="utf-8") as file:
            body = file.read()
        content_type = "text/css; charset=utf-8" if requested.endswith(".css") else "text/plain; charset=utf-8"
        return Response(HTTPStatus.OK, body, {"Content-Type": content_type})


app = Application()


class FrontController(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._process("GET")

    def do_POST(self) -> None:
        self._process("POST")

    def _process(self, method: str) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        request = Request(method, self.path, dict(self.headers), body)
        logging.info("HTTP %s %s", method, request.path)
        try:
            response = app.handle(request)
        except Exception:
            logging.exception("Unhandled request error")
            response = Response.html("<h1>500 Internal Server Error</h1>", 500)
        self.send_response(response.status)
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(response.body.encode("utf-8"))


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = HTTPServer((Config.HOST, Config.PORT), FrontController)
    logging.info("Server started at http://%s:%s", Config.HOST, Config.PORT)
    server.serve_forever()


if __name__ == "__main__":
    run()
