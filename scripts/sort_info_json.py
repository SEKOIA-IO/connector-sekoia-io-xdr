#!/usr/bin/env python3
"""Sort selected arrays in connector info.json for stable diffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def sort_info_json(file_path: Path) -> None:
    content = json.loads(file_path.read_text(encoding="utf-8"))

    configuration = content.get("configuration", {})
    fields = configuration.get("fields")
    if isinstance(fields, list):
        configuration["fields"] = sorted(fields, key=lambda item: item.get("name", ""))

    operations = content.get("operations")
    if isinstance(operations, list):
        content["operations"] = sorted(
            operations, key=lambda item: item.get("operation", "")
        )

    file_path.write_text(
        json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


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
    args = parser.parse_args()
    sort_info_json(Path(args.path))
