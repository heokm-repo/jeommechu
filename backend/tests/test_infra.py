from __future__ import annotations

from pathlib import Path
import unittest

from backend import database, http_io, static_files, static_server
from backend.infra import database as infra_database
from backend.infra import http_io as infra_http_io
from backend.infra.static_files import content_type_for, resolve_static_file


class InfraTest(unittest.TestCase):
    def test_database_wrapper_exports_infra_symbols(self) -> None:
        self.assertIs(database.connect, infra_database.connect)
        self.assertEqual(infra_database.SCHEMA_PATH.name, "schema.mysql.sql")
        self.assertTrue(infra_database.SCHEMA_PATH.exists())

    def test_http_wrapper_uses_infra_database_error(self) -> None:
        self.assertIs(http_io.IntegrityError, infra_database.IntegrityError)
        self.assertIs(http_io.write_json, infra_http_io.write_json)

    def test_static_file_helpers_resolve_content_type_and_traversal(self) -> None:
        root_dir = Path(__file__).resolve().parent

        self.assertEqual(content_type_for(Path("app.js")), "application/javascript; charset=utf-8")
        self.assertEqual(resolve_static_file(root_dir, ""), (root_dir / "index.html").resolve())
        self.assertIsNone(resolve_static_file(root_dir, "../server.py"))

    def test_static_wrappers_export_infra_symbols(self) -> None:
        self.assertIs(static_files.content_type_for, content_type_for)
        self.assertIs(static_server.content_type_for, content_type_for)


if __name__ == "__main__":
    unittest.main()