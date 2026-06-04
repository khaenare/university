import unittest

from app.core.request import Request
from app.core.response import Response
from app.core.router import Router


class DummyCommand:
    def process(self, request):
        return Response.html("ok")


class RouterTest(unittest.TestCase):
    def test_resolves_matching_route(self):
        router = Router()
        command = DummyCommand()
        router.add("GET", "/publications", command)

        route = router.resolve("GET", "/publications")

        self.assertIsNotNone(route)
        self.assertIs(route.command, command)

    def test_method_is_part_of_route(self):
        router = Router()
        router.add("POST", "/login", DummyCommand())

        self.assertIsNone(router.resolve("GET", "/login"))

    def test_dispatch_returns_404_for_unknown_route(self):
        response = Router().dispatch(Request("GET", "/missing", {}, ""))

        self.assertEqual(404, response.status)


if __name__ == "__main__":
    unittest.main()
