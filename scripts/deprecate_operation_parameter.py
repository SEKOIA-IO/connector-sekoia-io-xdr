#!/usr/bin/env python3
"""Deprecate one parameter in one operation in connector info.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts.cli_utils import configure_script_logger

DEFAULT_PATH = "sekoia-io-xdr/info.json"
logger = configure_script_logger(Path(__file__).name)


def normalize_deprecated_title(title: str, fallback_name: str) -> str:
    cleaned = title.strip()

    cleaned = re.sub(r"^\[\s*deprecated\s*\]\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\(\s*deprecated\s*\)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^deprecated\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)

    if not cleaned:
        cleaned = fallback_name

    return f"[Deprecated] {cleaned}"


def build_deprecated_parameter_description(replacement: str | None) -> str:
    if replacement:
        return f"Deprecated parameter. Use {replacement} parameter instead."
    return "Deprecated alias. There is no replacement."


def _find_operation(data: dict, operation_name: str) -> dict | None:
    for operation in data.get("operations", []):
        if operation.get("operation") == operation_name:
            return operation
    return None


def _find_parameter(operation: dict, parameter_name: str) -> dict | None:
    for parameter in operation.get("parameters", []):
        if parameter.get("name") == parameter_name:
            return parameter
    return None


def deprecate_operation_parameter(
    data: dict,
    operation_name: str,
    parameter_name: str,
    replacement: str | None = None,
) -> bool:
    operation = _find_operation(data, operation_name)
    if operation is None:
        raise ValueError(f"Operation not found: {operation_name}")

    parameter = _find_parameter(operation, parameter_name)
    if parameter is None:
        raise ValueError(
            f"Parameter '{parameter_name}' not found in operation '{operation_name}'"
        )

    changed = False

    expected_description = build_deprecated_parameter_description(replacement)
    if parameter.get("description") != expected_description:
        parameter["description"] = expected_description
        changed = True

    expected_title = normalize_deprecated_title(
        str(parameter.get("title", "")),
        fallback_name=parameter_name,
    )
    if parameter.get("title") != expected_title:
        parameter["title"] = expected_title
        changed = True

    return changed


def deprecate_parameter_in_file(
    file_path: Path,
    operation_name: str,
    parameter_name: str,
    replacement: str | None,
    check_only: bool,
) -> int:
    raw_content = file_path.read_text(encoding="utf-8")
    data = json.loads(raw_content)

    before = json.dumps(data, sort_keys=True)
    deprecate_operation_parameter(data, operation_name, parameter_name, replacement)
    after = json.dumps(data, sort_keys=True)
    changed = before != after

    if check_only:
        if changed:
            logger.error(
                (
                    "Fail: deprecated parameter metadata is not normalized for "
                    f"'{operation_name}.{parameter_name}'"
                ),
                extra={"color": "red"},
            )
            return 1

        logger.info(
            (
                "Success: deprecated parameter metadata already normalized for "
                f"'{operation_name}.{parameter_name}'"
            ),
            extra={"color": "green"},
        )
        return 0

    if not changed:
        logger.info(
            (
                "Success: deprecated parameter metadata already normalized for "
                f"'{operation_name}.{parameter_name}'"
            ),
            extra={"color": "green"},
        )
        return 0

    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info(
        (
            "Success: deprecated parameter metadata updated for "
            f"'{operation_name}.{parameter_name}'"
        ),
        extra={"color": "green"},
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Deprecate one operation parameter in connector info.json by applying "
            "canonical description/title conventions."
        )
    )
    parser.add_argument("operation", help="Operation name in info.json")
    parser.add_argument("parameter", help="Parameter name to deprecate")
    parser.add_argument(
        "--replacement",
        help="Replacement parameter name, if any",
        default=None,
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help=f"Path to info.json (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write the file; fail if metadata is not normalized.",
    )
    args = parser.parse_args()

    raise SystemExit(
        deprecate_parameter_in_file(
            Path(args.path),
            operation_name=args.operation,
            parameter_name=args.parameter,
            replacement=args.replacement,
            check_only=args.check,
        )
    )
