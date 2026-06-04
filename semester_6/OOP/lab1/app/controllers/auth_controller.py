from app.core.controller import Controller
from app.core.response import Response
from app.core.session import clear_session_cookie, session_cookie


class AuthController(Controller):
    def __init__(self, templates, auth_service, session_store) -> None:
        super().__init__(templates)
        self._auth_service = auth_service
        self._sessions = session_store

    def login_page(self, request) -> Response:
        return self.render("login.html", {"error": request.param("error")})

    def login(self, request) -> Response:
        user = self._auth_service.authenticate(request.param("username"), request.param("password"))
        if not user:
            return self.redirect("/login?error=invalid")
        response = self.redirect("/publications")
        response.headers["Set-Cookie"] = session_cookie(self._sessions.create(user.id))
        return response

    def logout(self, request) -> Response:
        cookie = request.cookies.get("SESSION_ID")
        self._sessions.delete(cookie.value if cookie else None)
        response = self.redirect("/login")
        response.headers["Set-Cookie"] = clear_session_cookie()
        return response
