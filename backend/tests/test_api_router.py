from __future__ import annotations

import unittest

from backend import api_router
from backend.utils import AuthenticationError


class ApiRouterTest(unittest.TestCase):
    def test_health_route(self) -> None:
        self.assertEqual(api_router.handle_get_api("/api/health", ""), (200, {"ok": True}))

    def test_unknown_get_route_returns_none_for_server_fallback(self) -> None:
        self.assertIsNone(api_router.handle_get_api("/api/missing", ""))

    def test_malformed_feedback_route_returns_not_found(self) -> None:
        self.assertEqual(api_router.handle_post_api("/api/recommendations/a/b/feedback", {}), (404, {"error": "Not found"}))

    def test_user_data_get_requires_session(self) -> None:
        with self.assertRaises(AuthenticationError):
            api_router.handle_get_api("/api/favorites", "user_id=user-1")

    def test_user_data_post_requires_session(self) -> None:
        with self.assertRaises(AuthenticationError):
            api_router.handle_post_api("/api/favorites", {"user_id": "user-1", "restaurant_id": "restaurant-1"})

    def test_recommendation_detail_requires_session(self) -> None:
        with self.assertRaises(AuthenticationError):
            api_router.handle_get_api("/api/recommendations/search-1", "")


if __name__ == "__main__":
    unittest.main()