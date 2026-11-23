"""Shared validation helpers for model-generated service results."""

from __future__ import annotations

from typing import Any


class ServiceResponseError(ValueError):
    """Raised when a model response does not match the expected schema."""


def require_text(data: dict[str, Any], key: str) -> str:
    """Return a non-empty string field or report an invalid model response."""
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ServiceResponseError(f"Model response field '{key}' must be a non-empty string.")
    return value.strip()


def require_text_list(data: dict[str, Any], key: str) -> list[str]:
    """Return a non-empty list of strings."""
    value = data.get(key)
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ServiceResponseError(f"Model response field '{key}' must be a non-empty list of strings.")
    return [item.strip() for item in value]
