from __future__ import annotations

import unittest

from backend.restaurant_service import search_options
from backend.schemas import RecommendationSearchRequest, RestaurantSearchRequest


class RecommendationSearchRequestTest(unittest.TestCase):
    def test_normalizes_recommendation_payload(self) -> None:
        request = RecommendationSearchRequest.from_payload({
            "user_id": " user-1 ",
            "emotion_state": " 든든한 음식 ",
            "search_context": "  야근 전 ",
            "contexts": [" 혼밥 ", "", None, "빠르게"],
            "address": " 서울 강남구 역삼동 ",
            "longitude": "127.1",
            "latitude": "37.5",
            "radius": "999999",
            "size": "0",
        })

        self.assertEqual(request.user_id, "user-1")
        self.assertEqual(request.emotion_state, "든든한 음식")
        self.assertEqual(request.search_context, "야근 전")
        self.assertEqual(request.contexts, ["혼밥", "빠르게"])
        self.assertEqual(request.address, "서울 강남구 역삼동")
        self.assertEqual(request.longitude, 127.1)
        self.assertEqual(request.latitude, 37.5)
        self.assertEqual(request.radius, 20000)
        self.assertEqual(request.size, 1)

    def test_requires_emotion_state(self) -> None:
        with self.assertRaises(ValueError):
            RecommendationSearchRequest.from_payload({"emotion_state": " "})


class RestaurantSearchRequestTest(unittest.TestCase):
    def test_defaults_and_bounds_restaurant_payload(self) -> None:
        request = RestaurantSearchRequest.from_payload({
            "query": " ",
            "radius": "0",
            "size": "99",
            "pages": "99",
            "sort": " ",
        })

        self.assertEqual(request.query, "음식점")
        self.assertEqual(request.radius, 1)
        self.assertEqual(request.size, 15)
        self.assertEqual(request.pages, 3)
        self.assertEqual(request.sort, "accuracy")

    def test_search_options_uses_normalized_schema_values(self) -> None:
        options = search_options({
            "query": " 돈까스 ",
            "address": "서울 강남구 역삼동",
            "longitude": "127.1",
            "latitude": "37.5",
            "radius": "2000",
            "size": "20",
            "pages": "2",
            "sort": "distance",
        })

        self.assertEqual(options["query"], "돈까스")
        self.assertEqual(options["address"], "서울 강남구 역삼동")
        self.assertEqual(options["longitude"], 127.1)
        self.assertEqual(options["latitude"], 37.5)
        self.assertEqual(options["radius"], 2000)
        self.assertEqual(options["size"], 15)
        self.assertEqual(options["max_pages"], 2)
        self.assertEqual(options["sort"], "distance")


if __name__ == "__main__":
    unittest.main()