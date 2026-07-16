from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from typing import Mapping

from apps.browser_product_console_runtime_app_1.runtime_lifecycle import (
    HardenedLoopbackHTTPServer,
    create_hardened_loopback_server,
    host_header_is_valid,
)

from .application import FCFWebConsoleApplication, WebConsoleResponse


@dataclass(frozen=True)
class FCFWebConsoleServerConfig:
    port: int = 8775
    host: str = "127.0.0.1"
    request_body_max_bytes: int = 1_048_576

    def __post_init__(self) -> None:
        if self.host != "127.0.0.1":
            raise ValueError("bind host must remain exactly 127.0.0.1")
        if isinstance(self.port, bool) or not 1024 <= int(self.port) <= 65535:
            raise ValueError("port must be between 1024 and 65535")
        if not 1024 <= int(self.request_body_max_bytes) <= 4_194_304:
            raise ValueError("request_body_max_bytes is outside the safe range")
        object.__setattr__(self, "port", int(self.port))
        object.__setattr__(
            self,
            "request_body_max_bytes",
            int(self.request_body_max_bytes),
        )


def create_fcf_web_console_server(
    config: FCFWebConsoleServerConfig,
    application: FCFWebConsoleApplication,
) -> HardenedLoopbackHTTPServer:
    class FCFWebConsoleRequestHandler(BaseHTTPRequestHandler):
        server_version = "FCFWebConsole"
        sys_version = ""
        protocol_version = "HTTP/1.1"

        def _send(self, response: WebConsoleResponse) -> None:
            self.send_response(response.status)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(response.body)))
            emitted = set()
            for name, value in response.headers:
                self.send_header(name, value)
                emitted.add(name.lower())
            if "connection" not in emitted:
                self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(response.body)
            self.close_connection = True

        def _error(self, status: int, message: str) -> None:
            self._send(
                WebConsoleResponse(
                    status=status,
                    content_type="application/json; charset=utf-8",
                    body=json.dumps(
                        {"error": message},
                        ensure_ascii=True,
                        sort_keys=True,
                    ).encode("utf-8"),
                )
            )

        def _host_is_valid(self) -> bool:
            return host_header_is_valid(
                tuple(self.headers.get_all("Host", [])),
                config.port,
            )

        def _origin_is_valid(self) -> bool:
            origins = self.headers.get_all("Origin", [])
            return len(origins) == 1 and origins[0] in {
                f"http://127.0.0.1:{config.port}",
                f"http://localhost:{config.port}",
            }

        def _parse_json_body(self) -> Mapping[str, object]:
            if self.headers.get("Transfer-Encoding") is not None:
                raise ValueError("transfer encoding is not allowed")
            content_types = self.headers.get_all("Content-Type", [])
            lengths = self.headers.get_all("Content-Length", [])
            if len(content_types) != 1 or not content_types[0].lower().startswith(
                "application/json"
            ):
                raise ValueError("application/json content type is required")
            if len(lengths) != 1 or not lengths[0].isdigit():
                raise ValueError("one numeric Content-Length is required")
            length = int(lengths[0])
            if length < 2 or length > config.request_body_max_bytes:
                raise ValueError("request body size is outside the safe range")
            raw_body = self.rfile.read(length)
            if len(raw_body) != length:
                raise ValueError("request body was truncated")
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("request body must be a UTF-8 JSON object") from exc
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            return payload

        def _handle(self) -> None:
            if self.client_address[0] != "127.0.0.1":
                self._error(403, "loopback peer required")
                return
            if not self._host_is_valid():
                self._error(400, "invalid loopback Host header")
                return
            if len(self.path.encode("utf-8")) > 4096:
                self._error(414, "request target is too long")
                return
            payload = None
            if self.command == "POST":
                if not self._origin_is_valid():
                    self._error(403, "same-origin POST required")
                    return
                try:
                    payload = self._parse_json_body()
                except ValueError as exc:
                    self._error(400, str(exc))
                    return
            try:
                response = application.dispatch(
                    self.command,
                    self.path,
                    payload,
                    peer_host=self.client_address[0],
                )
            except Exception:
                self._error(500, "internal application error")
                return
            self._send(response)

        do_GET = _handle
        do_HEAD = _handle
        do_POST = _handle

        def do_PUT(self) -> None:
            self._error(405, "method not allowed")

        do_DELETE = do_PUT
        do_PATCH = do_PUT
        do_OPTIONS = do_PUT
        do_TRACE = do_PUT
        do_CONNECT = do_PUT

        def log_message(self, format: str, *args: object) -> None:
            return

    server = create_hardened_loopback_server(
        config.host,
        config.port,
        FCFWebConsoleRequestHandler,
    )
    if server.server_address != ("127.0.0.1", config.port):
        server.server_close()
        raise RuntimeError("FCF Web Console did not bind to exact loopback")
    return server
