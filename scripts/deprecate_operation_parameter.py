#!/usr/bin/env python3
"""Deprecate one parameter in one operation in connector info.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.utils.cli_utils import configure_script_logger
from scripts.utils.deprecation_utils import (
    find_operation,
    find_parameter,
    normalize_deprecated_title,
)

DEFAULT_PATH = "sekoia_io_xdr/info.json"
logger = configure_script_logger(Path(__file__).name)


def build_deprecated_parameter_description(replacement: str | None) -> str:
    if replacement:
        return f"Deprecated parameter. Use {replacement} parameter instead."
    return "Deprecated alias. There is no replacement."


def _parse_replacement_reference(replacement: str) -> tuple[str | None, str]:
    cleaned = replacement.strip()
    if not cleaned:
        raise ValueError("Replacement parameter cannot be empty")

    if "." not in cleaned:
        return None, cleaned

    replacement_operation, replacement_parameter = cleaned.split(".", 1)
    replacement_operation = replacement_operation.strip()
    replacement_parameter = replacement_parameter.strip()
    if not replacement_operation or not replacement_parameter:
        raise ValueError(
            "Replacement parameter reference must be '<parameter>' or "
            "'<operation>.<parameter>'"
        )
    return replacement_operation, replacement_parameter


def _validate_replacement_parameter(
    data: dict,
    operation_name: str,
    replacement: str | None,
) -> str | None:
    if replacement is None:
        return None

    replacement_operation_name, replacement_parameter_name = (
        _parse_replacement_reference(replacement)
    )
    target_operation_name = replacement_operation_name or operation_name

    target_operation = find_operation(data, target_operation_name)
    if target_operation is None:
        raise ValueError(f"Replacement operation not found: {target_operation_name}")

    target_parameter = find_parameter(target_operation, replacement_parameter_name)
    if target_parameter is None:
        raise ValueError(
            "Replacement parameter "
            f"'{replacement_parameter_name}' not found in operation "
            f"'{target_operation_name}'"
        )

    return replacement_parameter_name


def deprecate_operation_parameter(
    data: dict,
    operation_name: str,
    parameter_name: str,
    replacement: str | None = None,
) -> bool:
    operation = find_operation(data, operation_name)
    if operation is None:
        raise ValueError(f"Operation not found: {operation_name}")

    parameter = find_parameter(operation, parameter_name)
    if parameter is None:
        raise ValueError(
            f"Parameter '{parameter_name}' not found in operation '{operation_name}'"
        )

    normalized_replacement = _validate_replacement_parameter(
        data,
        operation_name=operation_name,
        replacement=replacement,
    )

    changed = False

    expected_description = build_deprecated_parameter_description(
        normalized_replacement
    )
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
