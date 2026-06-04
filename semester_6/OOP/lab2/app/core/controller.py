from app.core.request import Request
from app.core.response import Response


class Controller:
    def __init__(self, templates) -> None:
        self._templates = templates

    def render(self, template_name: str, model: dict | None = None, status: int = 200) -> Response:
        return Response.html(self._templates.render(template_name, model or {}), status)

    def redirect(self, location: str) -> Response:
        return Response.redirect(location)

    def require_admin(self, request: Request) -> bool:
        return bool(request.user and request.user.is_admin)
