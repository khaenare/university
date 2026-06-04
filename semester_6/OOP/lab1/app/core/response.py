from dataclasses import dataclass, field
from http import HTTPStatus


@dataclass
class Response:
    status: int = HTTPStatus.OK
    body: str = ""
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def html(cls, body: str, status: int = HTTPStatus.OK) -> "Response":
        return cls(status=status, body=body, headers={"Content-Type": "text/html; charset=utf-8"})

    @classmethod
    def redirect(cls, location: str) -> "Response":
        return cls(status=HTTPStatus.FOUND, headers={"Location": location})

    @classmethod
    def not_found(cls) -> "Response":
        return cls.html("<h1>404 Not Found</h1>", HTTPStatus.NOT_FOUND)
