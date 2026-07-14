from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence, Tuple
from urllib.parse import urlsplit

from .runtime_hardening import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    RuntimeHardeningLimits,
)


_HEADER_NAME = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
_ALLOWED_METHODS = frozenset({"GET", "HEAD"})


@dataclass(frozen=True)
class RuntimeRequestAssessment:
    accepted: bool
    status: int
    reason_code: str
    message: str
    response_headers: Tuple[Tuple[str, str], ...] = ()


def _rejected(
    status: int,
    reason_code: str,
    message: str,
    response_headers: Tuple[Tuple[str, str], ...] = (),
) -> RuntimeRequestAssessment:
    return RuntimeRequestAssessment(
        accepted=False,
        status=status,
        reason_code=reason_code,
        message=message,
        response_headers=response_headers,
    )


def assess_runtime_request(
    method: object,
    raw_target: object,
    raw_headers: Sequence[Tuple[str, str]],
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> RuntimeRequestAssessment:
    if not isinstance(limits, RuntimeHardeningLimits):
        raise ValueError("limits must be RuntimeHardeningLimits")

    if (
        not isinstance(method, str)
        or not method
        or method != method.strip()
        or any(character.isspace() for character in method)
    ):
        return _rejected(400, "MALFORMED_METHOD", "Bad Request")

    normalized_method = method.upper()

    if normalized_method not in _ALLOWED_METHODS:
        return _rejected(
            405,
            "UNSUPPORTED_HTTP_METHOD",
            "Method Not Allowed",
            (("Allow", "GET, HEAD"),),
        )

    if (
        not isinstance(raw_target, str)
        or not raw_target
        or raw_target != raw_target.strip()
        or any(
            ord(character) < 32 or ord(character) == 127
            for character in raw_target
        )
    ):
        return _rejected(
            400,
            "MALFORMED_REQUEST_TARGET",
            "Bad Request",
        )

    if len(raw_target.encode("utf-8")) > limits.request_target_max_bytes:
        return _rejected(
            414,
            "REQUEST_TARGET_EXCEEDED",
            "URI Too Long",
        )

    if not raw_target.startswith("/"):
        return _rejected(
            400,
            "ABSOLUTE_REQUEST_TARGET",
            "Bad Request",
        )

    split_result = urlsplit(raw_target)

    if split_result.scheme or split_result.netloc or split_result.fragment:
        return _rejected(
            400,
            "MALFORMED_REQUEST_TARGET",
            "Bad Request",
        )

    if isinstance(raw_headers, (str, bytes)):
        return _rejected(400, "MALFORMED_HEADERS", "Bad Request")

    headers = tuple(raw_headers)

    if len(headers) > limits.header_count_max:
        return _rejected(
            431,
            "HEADER_COUNT_EXCEEDED",
            "Request Header Fields Too Large",
        )

    normalized_headers = []

    for item in headers:
        if not isinstance(item, tuple) or len(item) != 2:
            return _rejected(400, "MALFORMED_HEADERS", "Bad Request")

        name, value = item

        if (
            not isinstance(name, str)
            or not isinstance(value, str)
            or not name
            or not _HEADER_NAME.fullmatch(name)
            or "\r" in value
            or "\n" in value
            or "\x00" in value
        ):
            return _rejected(400, "MALFORMED_HEADERS", "Bad Request")

        if (
            len(f"{name}: {value}".encode("utf-8"))
            > limits.header_line_max_bytes
        ):
            return _rejected(
                431,
                "HEADER_LINE_EXCEEDED",
                "Request Header Fields Too Large",
            )

        normalized_headers.append((name.lower(), value))

    transfer_encoding = [
        value
        for name, value in normalized_headers
        if name == "transfer-encoding"
    ]

    if transfer_encoding:
        return _rejected(
            400,
            "UNSUPPORTED_TRANSFER_ENCODING",
            "Bad Request",
        )

    expect_values = [
        value
        for name, value in normalized_headers
        if name == "expect"
    ]

    if expect_values:
        return _rejected(
            417,
            "EXPECTATION_NOT_SUPPORTED",
            "Expectation Failed",
        )

    content_lengths = [
        value
        for name, value in normalized_headers
        if name == "content-length"
    ]

    if len(content_lengths) > 1:
        return _rejected(
            400,
            "AMBIGUOUS_CONTENT_LENGTH",
            "Bad Request",
        )

    if content_lengths:
        content_length = content_lengths[0]

        if not content_length or not content_length.isdigit():
            return _rejected(
                400,
                "INVALID_CONTENT_LENGTH",
                "Bad Request",
            )

        if int(content_length) != 0:
            return _rejected(
                413,
                "REQUEST_BODY_PRESENT",
                "Payload Too Large",
            )

    return RuntimeRequestAssessment(
        accepted=True,
        status=200,
        reason_code="ACCEPTED",
        message="Accepted",
    )
