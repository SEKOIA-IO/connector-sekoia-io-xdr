#!/usr/bin/env python3
"""Normalize connector info.json ordering for stable diffs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GREEN_BOLD = "\033[1;32m"
RESET = "\033[0m"
DEFAULT_PATH = "sekoia-io-xdr/info.json"

# Most lists keep their original order. Only these business lists are sorted.
LIST_SORT_KEYS = {
    ("configuration", "fields"): "name",
    ("operations",): "operation",
    ("operations", "parameters"): "name",
}


def sort_value(value, path: tuple[str, ...] = ()):
    # Sort every dict by key, recursively.
    if isinstance(value, dict):
        return {key: sort_value(value[key], path + (key,)) for key in sorted(value)}

    if isinstance(value, list):
        items = [sort_value(item, path) for item in value]

        # Apply explicit ordering rules only where the manifest needs them.
        sort_key = LIST_SORT_KEYS.get(path)
        if sort_key:
            return sorted(items, key=lambda item: item.get(sort_key, ""))

        return items

    return value


def build_sorted_content(raw_content: str) -> str:
    return (
        json.dumps(sort_value(json.loads(raw_content)), indent=2, ensure_ascii=False)
        + "\n"
    )


def sort_info_json(file_path: Path, check_only: bool = False) -> int:
    original = file_path.read_text(encoding="utf-8")
    sorted_content = build_sorted_content(original)

    if check_only:
        if original != sorted_content:
            print(
                f"Failed: file {file_path} is not sorted\nRun this command to fix it:\nuv run python scripts/sort_info_json.py",
                file=sys.stderr,
            )
            return 1
        print(f"{GREEN_BOLD}Success: {file_path} is already sorted.{RESET}")
        return 0

    file_path.write_text(sorted_content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Sort all dict keys alphabetically, sort `configuration.fields` and "
            "each operation's `parameters` by `name`, and sort `operations` by "
            "`operation` in a connector info.json file."
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
        help="Do not write the file; fail if content is not already sorted.",
    )
    args = parser.parse_args()
    raise SystemExit(sort_info_json(Path(args.path), check_only=args.check))
