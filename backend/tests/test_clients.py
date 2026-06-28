from __future__ import annotations

import unittest

from backend.clients import build_kakao_search_params, convert_to_grid, postposition_eul_reul


class ClientsTest(unittest.TestCase):
    def test_category_search_is_used_for_generic_food_query_with_center(self) -> None:
        path, params = build_kakao_search_params("음식점", "", 127.0, 37.0, 1500, "accuracy", 1, 10)

        self.assertEqual(path, "/search/category.json")
        self.assertEqual(params["category_group_code"], "FD6")
        self.assertEqual(params["x"], 127.0)
        self.assertEqual(params["y"], 37.0)

    def test_keyword_search_includes_address_when_query_is_specific(self) -> None:
        path, params = build_kakao_search_params("돈까스", "서울 강남구 역삼동", None, None, 1500, "distance", 1, 10)

        self.assertEqual(path, "/search/keyword.json")
        self.assertEqual(params["query"], "서울 강남구 역삼동 돈까스")
        self.assertIsNone(params["radius"])
        self.assertEqual(params["sort"], "accuracy")

    def test_weather_grid_conversion_is_exported(self) -> None:
        self.assertEqual(convert_to_grid(37.5, 127.0), (60, 125))

    def test_postposition_helper_handles_final_consonant(self) -> None:
        self.assertEqual(postposition_eul_reul("밥"), "을")
        self.assertEqual(postposition_eul_reul("커피"), "를")


if __name__ == "__main__":
    unittest.main()