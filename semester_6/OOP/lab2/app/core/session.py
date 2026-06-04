import secrets
from http.cookies import SimpleCookie


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, int] = {}

    def create(self, user_id: int) -> str:
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = user_id
        return session_id

    def get_user_id(self, session_id: str | None) -> int | None:
        if not session_id:
            return None
        return self._sessions.get(session_id)

    def delete(self, session_id: str | None) -> None:
        if session_id:
            self._sessions.pop(session_id, None)


def session_cookie(session_id: str, max_age: int = 86400) -> str:
    cookie = SimpleCookie()
    cookie["SESSION_ID"] = session_id
    cookie["SESSION_ID"]["httponly"] = True
    cookie["SESSION_ID"]["path"] = "/"
    cookie["SESSION_ID"]["max-age"] = max_age
    return cookie.output(header="").strip()


def clear_session_cookie() -> str:
    return session_cookie("", 0)
