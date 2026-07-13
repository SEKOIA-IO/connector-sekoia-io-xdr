#!/usr/bin/env python3
"""Normalize deprecated operation parameter metadata in connector info.json."""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

GREEN_BOLD = "\033[1;32m"
RED_BOLD = "\033[1;31m"
RESET = "\033[0m"
DEFAULT_PATH = "sekoia-io-xdr/info.json"

logger = logging.getLogger(Path(__file__).name)


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = getattr(record, "color", None)

        if color == "green":
            return f"{GREEN_BOLD}{message}{RESET}"
        if color == "red":
            return f"{RED_BOLD}{message}{RESET}"
        return message


def extract_replacement_alias(description: str) -> str | None:
    # Example: "Deprecated alias. Use match[status_uuid] instead."
    # Example: "Deprecated: use UUID instead. ..."
    match = re.search(r"\buse\s+(.+?)\s+instead\b", description, flags=re.IGNORECASE)
    if not match:
        return None

    alias = match.group(1).strip()
    alias = alias.strip("`\"' ")
    return alias or None


def normalize_title(title: str, fallback_name: str) -> str:
    cleaned = title.strip()

    cleaned = re.sub(r"^\[\s*deprecated\s*\]\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\(\s*deprecated\s*\)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^deprecated\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)

    if not cleaned:
        cleaned = fallback_name

    return f"[Deprecated] {cleaned}"


def normalize_deprecated_parameters(data: dict) -> bool:
    changed = False

    for operation in data.get("operations", []):
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

            replacement = extract_replacement_alias(description)
            if replacement:
                expected_description = f"Deprecated alias. Use {replacement} instead."
            else:
                expected_description = "Deprecated alias. There is no replacement."

            if parameter.get("description") != expected_description:
                parameter["description"] = expected_description
                changed = True

            expected_title = normalize_title(title, str(parameter.get("name", "Parameter")))
            if parameter.get("title") != expected_title:
                parameter["title"] = expected_title
                changed = True

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
                "uv run python scripts/normalize_deprecated_parameters.py",
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
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter(
            "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False

    parser = argparse.ArgumentParser(
        description=(
            "Normalize deprecated operation parameters in connector info.json by "
            "enforcing canonical description/title conventions."
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
