from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    from .api_router import handle_delete_api, handle_get_api, handle_post_api, not_found
    from .infra.database import init_db
    from .infra.http_io import read_cookies, read_json, write_api_response, write_error_response, write_json
    from .infra.static_server import serve_static_file
except ImportError:
    from api_router import handle_delete_api, handle_get_api, handle_post_api, not_found
    from infra.database import init_db
    from infra.http_io import read_cookies, read_json, write_api_response, write_error_response, write_json
    from infra.static_server import serve_static_file

BASE_DIR = Path(__file__).resolve().parent


def load_env() -> None:
    env_path = BASE_DIR.parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class JeommechuHandler(BaseHTTPRequestHandler):
    server_version = "JeommechuAPI/0.1"

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        write_json(self, 204, {})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/"):
                write_api_response(self, handle_get_api(parsed.path, parsed.query, read_cookies(self)), not_found())
                return
            serve_static_file(self, BASE_DIR.parent, parsed.path)
        except Exception as exc:
            write_error_response(self, exc)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        try:
            write_api_response(self, handle_delete_api(parsed.path, parsed.query, read_cookies(self)), not_found())
        except Exception as exc:
            write_error_response(self, exc)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = read_json(self)
            write_api_response(self, handle_post_api(parsed.path, payload, read_cookies(self)), not_found())
        except Exception as exc:
            write_error_response(self, exc)

    def log_message(self, format: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), format % args))


def main() -> None:
    load_env()
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), JeommechuHandler)
    print("Jeommechu API running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()