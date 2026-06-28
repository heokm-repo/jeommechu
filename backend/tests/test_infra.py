from __future__ import annotations

from pathlib import Path
import unittest

from backend.infra import database as infra_database
from backend.infra import http_io as infra_http_io
from backend.infra import static_files, static_server
from backend.infra.static_files import content_type_for, resolve_static_file


class InfraTest(unittest.TestCase):
    def test_database_schema_path_points_to_backend_schema(self) -> None:
        self.assertEqual(infra_database.SCHEMA_PATH.name, "schema.mysql.sql")
        self.assertTrue(infra_database.SCHEMA_PATH.exists())

    def test_http_io_uses_infra_database_error(self) -> None:
        self.assertIs(infra_http_io.IntegrityError, infra_database.IntegrityError)
        self.assertTrue(callable(infra_http_io.write_json))

    def test_static_file_helpers_resolve_content_type_and_traversal(self) -> None:
        root_dir = Path(__file__).resolve().parent

        self.assertEqual(content_type_for(Path("app.js")), "application/javascript; charset=utf-8")
        self.assertEqual(resolve_static_file(root_dir, ""), (root_dir / "index.html").resolve())
        self.assertIsNone(resolve_static_file(root_dir, "../server.py"))

    def test_static_server_uses_static_file_helpers(self) -> None:
        self.assertIs(static_server.content_type_for, static_files.content_type_for)
        self.assertIs(static_server.resolve_static_file, static_files.resolve_static_file)


if __name__ == "__main__":
    unittest.main()