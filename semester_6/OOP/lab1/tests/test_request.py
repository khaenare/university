import unittest

from app.core.request import Request


class RequestTest(unittest.TestCase):
    def test_parses_query_form_and_cookies(self):
        request = Request(
            "POST",
            "/subscriptions?source=list",
            {"Cookie": "SESSION_ID=abc"},
            "publication_id=10&months=3",
        )

        self.assertEqual("/subscriptions", request.path)
        self.assertEqual("list", request.param("source"))
        self.assertEqual("10", request.param("publication_id"))
        self.assertEqual("abc", request.cookies["SESSION_ID"].value)


if __name__ == "__main__":
    unittest.main()
