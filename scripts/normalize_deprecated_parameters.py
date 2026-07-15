#!/usr/bin/env python3
"""Normalize deprecated operation parameter metadata in connector info.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts.cli_utils import configure_script_logger
from scripts.deprecate_operation import deprecate_operation
from scripts.deprecate_operation_parameter import deprecate_operation_parameter

DEFAULT_PATH = "sekoia-io-xdr/info.json"
logger = configure_script_logger(Path(__file__).name)


def extract_replacement_alias(description: str) -> str | None:
    # Example: "Deprecated parameter. Use match[status_uuid] parameter instead."
    # Example: "Deprecated: use UUID instead. ..."
    match = re.search(
        r"\buse\s+(.+?)\s+(?:parameter\s+)?instead\b",
        description,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    alias = match.group(1).strip()
    alias = alias.strip("`\"' ")
    return alias or None


def extract_replacement_operation(description: str) -> str | None:
    # Example: "Deprecated operation. Use revoke_assetv2 operation instead."
    match = re.search(
        r"\buse\s+(.+?)\s+operation\s+instead\b",
        description,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    replacement = match.group(1).strip().strip("`\"' ")
    return replacement or None


def normalize_deprecated_parameters(data: dict) -> bool:
    changed = False

    for operation in data.get("operations", []):
        operation_name = str(operation.get("operation", ""))

        operation_description = str(operation.get("description", ""))
        operation_title = str(operation.get("title", ""))
        is_operation_deprecated = (
            "deprecated" in operation_description.lower()
            or operation_title.lower().startswith("[deprecated]")
            or "(deprecated)" in operation_title.lower()
        )
        if is_operation_deprecated and operation_name:
            replacement_operation = extract_replacement_operation(operation_description)
            changed |= deprecate_operation(
                data,
                operation_name=operation_name,
                replacement=replacement_operation,
            )

        for parameter in operation.get("parameters", []):
            description = str(parameter.get("description", ""))
            title = str(parameter.get("title", ""))

            is_deprecated = (
                "deprecated" in description.lower()
                or title.lower().startswith("[deprecated]")
                or "(deprecated)" in title.lower()
            )

            if not is_deprecated:
                continue

            parameter_name = str(parameter.get("name", ""))
            if not operation_name or not parameter_name:
                continue

            replacement = extract_replacement_alias(description)
            changed |= deprecate_operation_parameter(
                data,
                operation_name=operation_name,
                parameter_name=parameter_name,
                replacement=replacement,
            )

    return changed


def normalize_file(file_path: Path, check_only: bool = False) -> int:
    raw_content = file_path.read_text(encoding="utf-8")
    data = json.loads(raw_content)

    changed = normalize_deprecated_parameters(data)
    normalized_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if check_only:
        if changed:
            logger.error(
                f"Fail: file {file_path} has non-normalized deprecated parameters",
                extra={"color": "red"},
            )
            logger.info(
                "Run this command to fix it:\n"
                "uv run python -m scripts.normalize_deprecated_parameters",
                extra={"color": None},
            )
            return 1

        logger.info(
            f"Success: file {file_path} has normalized deprecated parameters",
            extra={"color": "green"},
        )
        return 0

    if not changed:
        logger.info(
            f"Success: file {file_path} already has normalized deprecated parameters",
            extra={"color": "green"},
        )
        return 0

    file_path.write_text(normalized_content, encoding="utf-8")
    logger.info(
        f"Success: file {file_path} deprecated parameters have been normalized",
        extra={"color": "green"},
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Normalize deprecated operation and parameter metadata in connector "
            "info.json by enforcing canonical description/title conventions."
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_PATH,
        help=f"Path to info.json (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write the file; fail if deprecated metadata is not normalized.",
    )
    args = parser.parse_args()

    raise SystemExit(normalize_file(Path(args.path), check_only=args.check))
