import logging
from dataclasses import dataclass
from typing import Protocol

from app.core.request import Request
from app.core.response import Response


class Command(Protocol):
    def process(self, request: Request) -> Response: ...


@dataclass(frozen=True)
class Route:
    method: str
    path: str
    command: Command
    auth_required: bool = True


class Router:
    def __init__(self) -> None:
        self._routes: list[Route] = []

    def add(self, method: str, path: str, command: Command, auth_required: bool = True) -> None:
        self._routes.append(Route(method.upper(), path, command, auth_required))

    def resolve(self, method: str, path: str) -> Route | None:
        logging.debug("Resolving route %s %s", method, path)
        for route in self._routes:
            if route.method == method.upper() and route.path == path:
                return route
        return None

    def dispatch(self, request: Request) -> Response:
        route = self.resolve(request.method, request.path)
        if route is None:
            logging.warning("Route not found: %s %s", request.method, request.path)
            return Response.not_found()
        return route.command.process(request)
