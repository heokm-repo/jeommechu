from __future__ import annotations

import unittest

from backend import activity_repository, restaurant_repository
from backend.repositories.activity_repository import recommendation_restaurant_from_row
from backend.repositories.restaurant_repository import search_cache_key


class RepositoriesTest(unittest.TestCase):
    def test_legacy_restaurant_repository_wrapper_exports_same_function(self) -> None:
        self.assertIs(restaurant_repository.search_cache_key, search_cache_key)

    def test_search_cache_key_is_stable_for_same_payload(self) -> None:
        first = search_cache_key("돈까스", 127.0, 37.0, 1500, "accuracy")
        second = search_cache_key("돈까스", 127.0, 37.0, 1500, "accuracy")

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_activity_repository_wrapper_exports_same_function(self) -> None:
        self.assertIs(activity_repository.recommendation_restaurant_from_row, recommendation_restaurant_from_row)

    def test_recommendation_restaurant_from_row_maps_raw_data(self) -> None:
        row = {
            "restaurant_id": "r1",
            "external_provider": "KAKAO",
            "external_place_id": "p1",
            "name": "가게",
            "category": "음식점",
            "phone": "02-0000",
            "address": "서울",
            "road_address": "서울 도로명",
            "latitude": 37.0,
            "longitude": 127.0,
            "raw_data": '{"place_url":"https://place.example","distance":"120"}',
        }

        restaurant = recommendation_restaurant_from_row(row)

        self.assertEqual(restaurant["id"], "r1")
        self.assertEqual(restaurant["place_url"], "https://place.example")
        self.assertEqual(restaurant["distance"], "120")


if __name__ == "__main__":
    unittest.main()