#!/usr/bin/env python3
"""Deprecate one operation in connector info.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.utils.cli_utils import configure_script_logger
from scripts.utils.deprecation_utils import find_operation, normalize_deprecated_title

DEFAULT_PATH = "sekoia-io-xdr/info.json"
logger = configure_script_logger(Path(__file__).name)


def build_deprecated_operation_description(replacement: str | None) -> str:
    if replacement:
        return f"Deprecated operation. Use {replacement} operation instead."
    return "Deprecated operation. There is no replacement."


def _validate_replacement_operation(data: dict, replacement: str | None) -> None:
    if replacement is None:
        return

    if not replacement.strip():
        raise ValueError("Replacement operation cannot be empty")

    if find_operation(data, replacement.strip()) is None:
        raise ValueError(f"Replacement operation not found: {replacement}")


def deprecate_operation(
    data: dict,
    operation_name: str,
    replacement: str | None = None,
) -> bool:
    operation = find_operation(data, operation_name)
    if operation is None:
        raise ValueError(f"Operation not found: {operation_name}")

    _validate_replacement_operation(data, replacement)

    changed = False

    expected_description = build_deprecated_operation_description(replacement)
    if operation.get("description") != expected_description:
        operation["description"] = expected_description
        changed = True

    expected_title = normalize_deprecated_title(
        str(operation.get("title", "")),
        fallback_name=operation_name,
    )
    if operation.get("title") != expected_title:
        operation["title"] = expected_title
        changed = True

    return changed


def deprecate_operation_in_file(
    file_path: Path,
    operation_name: str,
    replacement: str | None,
    check_only: bool,
) -> int:
    raw_content = file_path.read_text(encoding="utf-8")
    data = json.loads(raw_content)

    before = json.dumps(data, sort_keys=True)
    deprecate_operation(data, operation_name, replacement)
    after = json.dumps(data, sort_keys=True)
    changed = before != after

    if check_only:
        if changed:
            logger.error(
                (
                    "Fail: deprecated operation metadata is not normalized for "
                    f"'{operation_name}'"
                ),
                extra={"color": "red"},
            )
            return 1

        logger.info(
            (
                "Success: deprecated operation metadata already normalized for "
                f"'{operation_name}'"
            ),
            extra={"color": "green"},
        )
        return 0

    if not changed:
        logger.info(
            (
                "Success: deprecated operation metadata already normalized for "
                f"'{operation_name}'"
            ),
            extra={"color": "green"},
        )
        return 0

    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info(
        f"Success: deprecated operation metadata updated for '{operation_name}'",
        extra={"color": "green"},
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Deprecate one operation in connector info.json by applying canonical "
            "description/title conventions."
        )
    )
    parser.add_argument("operation", help="Operation name in info.json")
    parser.add_argument(
        "--replacement",
        help="Replacement operation name, if any",
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
        deprecate_operation_in_file(
            Path(args.path),
            operation_name=args.operation,
            replacement=args.replacement,
            check_only=args.check,
        )
    )
