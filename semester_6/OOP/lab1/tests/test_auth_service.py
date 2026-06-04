import unittest

from app.models.user import User
from app.services.auth_service import AuthService


class FakeUserDao:
    def __init__(self, user=None):
        self.user = user

    def find_by_username(self, username):
        return self.user if self.user and self.user.username == username else None


class AuthServiceTest(unittest.TestCase):
    def test_authenticate_valid_credentials(self):
        password_hash = AuthService.hash_password("password")
        service = AuthService(FakeUserDao(User(1, "reader", password_hash, "reader")))

        user = service.authenticate("reader", "password")

        self.assertIsNotNone(user)
        self.assertEqual("reader", user.username)

    def test_authenticate_invalid_password(self):
        password_hash = AuthService.hash_password("password")
        service = AuthService(FakeUserDao(User(1, "reader", password_hash, "reader")))

        self.assertIsNone(service.authenticate("reader", "wrong"))


if __name__ == "__main__":
    unittest.main()
