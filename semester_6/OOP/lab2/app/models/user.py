from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    password_hash: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
