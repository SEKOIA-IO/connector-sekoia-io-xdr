"""Shared helpers for deprecated operation/parameter metadata."""

from __future__ import annotations

import re


def normalize_deprecated_title(title: str, fallback_name: str) -> str:
    cleaned = strip_deprecated_title_prefix(title)

    if not cleaned:
        cleaned = fallback_name

    return f"[Deprecated] {cleaned}"


def strip_deprecated_title_prefix(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"^\[\s*deprecated\s*\]\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\(\s*deprecated\s*\)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^deprecated\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def find_operation(data: dict, operation_name: str) -> dict | None:
    for operation in data.get("operations", []):
        if operation.get("operation") == operation_name:
            return operation
    return None


def find_parameter(operation: dict, parameter_name: str) -> dict | None:
    for parameter in operation.get("parameters", []):
        if parameter.get("name") == parameter_name:
            return parameter
    return None
