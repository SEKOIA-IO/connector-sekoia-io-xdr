#!/usr/bin/env python3
"""Sort selected arrays in connector info.json for stable diffs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GREEN_BOLD = "\033[1;32m"
RESET = "\033[0m"


def build_sorted_content(raw_content: str) -> str:
    content = json.loads(raw_content)

    configuration = content.get("configuration", {})
    fields = configuration.get("fields")
    if isinstance(fields, list):
        configuration["fields"] = sorted(fields, key=lambda item: item.get("name", ""))

    operations = content.get("operations")
    if isinstance(operations, list):
        content["operations"] = sorted(
            operations, key=lambda item: item.get("operation", "")
        )

    return json.dumps(content, indent=2, ensure_ascii=False) + "\n"


def sort_info_json(file_path: Path, check_only: bool = False) -> int:
    original = file_path.read_text(encoding="utf-8")
    sorted_content = build_sorted_content(original)

    if check_only:
        if original != sorted_content:
            print(
                f"{file_path} is not sorted. Run: uv run python scripts/sort_info_json.py",
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
            "Sort `configuration.fields` by `name` and `operations` by `operation` "
            "in a connector info.json file."
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="sekoia-io-xdr/info.json",
        help="Path to info.json (default: sekoia-io-xdr/info.json)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write the file; fail if content is not already sorted.",
    )
    args = parser.parse_args()
    raise SystemExit(sort_info_json(Path(args.path), check_only=args.check))
