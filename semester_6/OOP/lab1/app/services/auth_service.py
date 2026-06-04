import hashlib
import hmac
import logging

from app.models.user import User


class AuthService:
    def __init__(self, user_dao) -> None:
        self._user_dao = user_dao

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def authenticate(self, username: str, password: str) -> User | None:
        user = self._user_dao.find_by_username(username)
        password_hash = self.hash_password(password)
        if user and hmac.compare_digest(user.password_hash, password_hash):
            logging.info("User %s authenticated", username)
            return user
        logging.warning("Failed login for %s", username)
        return None
