from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qs, urlparse


@dataclass
class Request:
    method: str
    raw_path: str
    headers: dict[str, str]
    body: str = ""
    path: str = field(init=False)
    query: dict[str, list[str]] = field(init=False)
    form: dict[str, str] = field(init=False)
    cookies: SimpleCookie = field(init=False)
    user: Any = None

    def __post_init__(self) -> None:
        parsed = urlparse(self.raw_path)
        self.path = parsed.path
        self.query = parse_qs(parsed.query)
        self.form = {k: v[0] for k, v in parse_qs(self.body).items()}
        self.cookies = SimpleCookie(self.headers.get("Cookie", ""))

    def param(self, name: str, default: str = "") -> str:
        return self.form.get(name) or (self.query.get(name, [default])[0])
