#!/usr/bin/env python3
"""Sync connector requirements.txt with the current uv.lock export."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from scripts.utils.cli_utils import configure_script_logger

DEFAULT_PATH = "sekoia-io-xdr/requirements.txt"
logger = configure_script_logger(Path(__file__).name)


def _build_expected_requirements() -> str:
    command = [
        "uv",
        "export",
        "--format",
        "requirements.txt",
        "--no-hashes",
        "--no-dev",
        "--frozen",
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def sync_requirements_txt(file_path: Path, check_only: bool = False) -> int:
    expected = _build_expected_requirements()

    if file_path.exists():
        current = file_path.read_text(encoding="utf-8")
    else:
        current = ""

    if check_only:
        if current != expected:
            logger.error(
                f"Fail: file {file_path} is not synchronized with uv.lock",
                extra={"color": "red"},
            )
            logger.info(
                "Run this command to fix it:\n"
                "uv run python -m scripts.sync_requirements_txt",
                extra={"color": None},
            )
            return 1

        logger.info(
            f"Success: file {file_path} is synchronized with uv.lock",
            extra={"color": "green"},
        )
        return 0

    if current == expected:
        logger.info(
            f"Success: file {file_path} is already synchronized with uv.lock",
            extra={"color": "green"},
        )
        return 0

    file_path.write_text(expected, encoding="utf-8")
    logger.info(
        f"Success: file {file_path} has been synchronized with uv.lock",
        extra={"color": "green"},
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize connector requirements.txt with uv.lock by exporting "
            "runtime dependencies using uv export."
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_PATH,
        help=f"Path to requirements.txt (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write the file; fail if it is not synchronized.",
    )
    args = parser.parse_args()
    raise SystemExit(sync_requirements_txt(Path(args.path), check_only=args.check))
