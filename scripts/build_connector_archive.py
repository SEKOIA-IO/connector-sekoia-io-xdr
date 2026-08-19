#!/usr/bin/env python3
"""Build a FortiSOAR connector .tgz archive from the packaging directory."""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

from scripts.sync_requirements_txt import sync_requirements_txt
from scripts.utils.cli_utils import configure_script_logger

DEFAULT_CONNECTOR_DIR = Path("sekoia-io-xdr")
DEFAULT_DIST_DIR = Path("dist")
IGNORED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tmp",
    ".git",
}
logger = configure_script_logger(Path(__file__).name)


def _read_connector_metadata(connector_dir: Path) -> tuple[str, str]:
    info_path = connector_dir / "info.json"
    if not info_path.exists():
        raise FileNotFoundError(f"Missing required file: {info_path}")

    payload = json.loads(info_path.read_text(encoding="utf-8"))
    name = str(payload.get("name", "")).strip()
    version = str(payload.get("version", "")).strip()

    if not name:
        raise ValueError("Invalid info.json: missing 'name'")
    if not version:
        raise ValueError("Invalid info.json: missing 'version'")

    if connector_dir.name != name:
        raise ValueError(
            "Invalid packaging layout: connector folder name "
            f"'{connector_dir.name}' must match info.json name '{name}'"
        )

    return name, version


def _should_skip(path: Path) -> bool:
    if any(part in IGNORED_PARTS for part in path.parts):
        return True
    if path.name.endswith(".pyc"):
        return True
    return False


def build_connector_archive(
    connector_dir: Path,
    output_dir: Path,
    archive_name: str | None,
    check_requirements: bool,
) -> Path:
    if check_requirements:
        check_result = sync_requirements_txt(
            connector_dir / "requirements.txt", check_only=True
        )
        if check_result != 0:
            raise RuntimeError(
                "requirements.txt is not synchronized with uv.lock. "
                "Run: uv run python -m scripts.sync_requirements_txt"
            )

    connector_name, version = _read_connector_metadata(connector_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    final_name = archive_name or f"{connector_name}-{version}.tgz"
    archive_path = output_dir / final_name

    root_parent = connector_dir.parent
    with tarfile.open(archive_path, mode="w:gz") as tar:
        tar.add(connector_dir, arcname=connector_dir.name, recursive=False)

        for path in sorted(connector_dir.rglob("*")):
            if _should_skip(path):
                continue
            arcname = str(path.relative_to(root_parent))
            tar.add(path, arcname=arcname, recursive=False)

    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a .tgz archive for the FortiSOAR connector package " "directory."
        )
    )
    parser.add_argument(
        "--connector-dir",
        default=str(DEFAULT_CONNECTOR_DIR),
        help=f"Connector directory to package (default: {DEFAULT_CONNECTOR_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_DIST_DIR),
        help=f"Output directory for generated archive (default: {DEFAULT_DIST_DIR})",
    )
    parser.add_argument(
        "--archive-name",
        default=None,
        help="Optional custom archive name (must end with .tgz).",
    )
    parser.add_argument(
        "--skip-requirements-check",
        action="store_true",
        help="Skip pre-check that requirements.txt is synchronized with uv.lock.",
    )
    args = parser.parse_args()

    archive_name = args.archive_name
    if archive_name and not archive_name.endswith(".tgz"):
        raise SystemExit("--archive-name must end with .tgz")

    archive_path = build_connector_archive(
        connector_dir=Path(args.connector_dir),
        output_dir=Path(args.output_dir),
        archive_name=archive_name,
        check_requirements=not args.skip_requirements_check,
    )

    logger.info(
        f"Success: archive generated at {archive_path}",
        extra={"color": "green"},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
