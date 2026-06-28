from __future__ import annotations

import unittest

from backend.services.auth_service import hash_password, verify_password
from backend.services.restaurant_service import search_options
from backend.services.user_service import create_guest_user


class ServicesTest(unittest.TestCase):
    def test_restaurant_search_options_are_available_from_services_package(self) -> None:
        options = search_options({"query": " 돈까스 ", "longitude": "127", "latitude": "37"})

        self.assertEqual(options["query"], "돈까스")
        self.assertEqual(options["longitude"], 127.0)
        self.assertEqual(options["latitude"], 37.0)

    def test_auth_password_hash_round_trip(self) -> None:
        stored_hash = hash_password("secret1")

        self.assertTrue(verify_password("secret1", stored_hash))
        self.assertFalse(verify_password("wrong1", stored_hash))

    def test_user_service_exposes_guest_creation_entrypoint(self) -> None:
        self.assertTrue(callable(create_guest_user))


if __name__ == "__main__":
    unittest.main()