from app.core.controller import Controller
from app.core.response import Response


class PublicationController(Controller):
    def __init__(self, templates, publication_service) -> None:
        super().__init__(templates)
        self._service = publication_service

    def index(self, request) -> Response:
        return self.render("publications.html", {
            "user": request.user,
            "publications": self._service.list_publications(),
        })

    def new(self, request) -> Response:
        if not self.require_admin(request):
            return Response.html("<h1>403 Forbidden</h1>", 403)
        return self.render("publication_form.html", {"user": request.user, "publication": None})

    def create(self, request) -> Response:
        if not self.require_admin(request):
            return Response.html("<h1>403 Forbidden</h1>", 403)
        self._service.create(
            request.param("title"),
            request.param("publisher"),
            request.param("period_months"),
            request.param("price"),
        )
        return self.redirect("/publications")

    def update(self, request) -> Response:
        if not self.require_admin(request):
            return Response.html("<h1>403 Forbidden</h1>", 403)
        self._service.update(
            request.param("id"),
            request.param("title"),
            request.param("publisher"),
            request.param("period_months"),
            request.param("price"),
        )
        return self.redirect("/publications")

    def delete(self, request) -> Response:
        if not self.require_admin(request):
            return Response.html("<h1>403 Forbidden</h1>", 403)
        self._service.delete(request.param("id"))
        return self.redirect("/publications")
