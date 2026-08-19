#!/usr/bin/env python3
"""Build FortiSOAR connector archives (.tgz and .zip) from the packaging directory."""

from __future__ import annotations

import argparse
import json
import tarfile
import zipfile
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


def _build_tgz_archive(
    connector_dir: Path,
    output_dir: Path,
    archive_name: str,
) -> Path:
    archive_path = output_dir / archive_name
    root_parent = connector_dir.parent

    with tarfile.open(archive_path, mode="w:gz") as tar:
        tar.add(connector_dir, arcname=connector_dir.name, recursive=False)

        for path in sorted(connector_dir.rglob("*")):
            if _should_skip(path):
                continue
            arcname = str(path.relative_to(root_parent))
            tar.add(path, arcname=arcname, recursive=False)

    return archive_path


def _build_zip_archive(
    connector_dir: Path,
    output_dir: Path,
    archive_name: str,
) -> Path:
    archive_path = output_dir / archive_name
    root_parent = connector_dir.parent

    with zipfile.ZipFile(
        archive_path, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for path in sorted(connector_dir.rglob("*")):
            if _should_skip(path):
                continue
            if path.is_dir():
                continue
            arcname = str(path.relative_to(root_parent))
            zf.write(path, arcname=arcname)

    return archive_path


def build_connector_archives(
    connector_dir: Path,
    output_dir: Path,
    tgz_name: str | None,
    zip_name: str | None,
    check_requirements: bool,
) -> tuple[Path, Path]:
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

    final_tgz_name = tgz_name or f"{connector_name}-{version}.tgz"
    final_zip_name = zip_name or f"{connector_name}-{version}.zip"

    if not final_tgz_name.endswith(".tgz"):
        raise ValueError("tgz archive name must end with .tgz")
    if not final_zip_name.endswith(".zip"):
        raise ValueError("zip archive name must end with .zip")

    tgz_path = _build_tgz_archive(connector_dir, output_dir, final_tgz_name)
    zip_path = _build_zip_archive(connector_dir, output_dir, final_zip_name)
    return tgz_path, zip_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate both .tgz and .zip archives for the FortiSOAR connector "
            "package directory."
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
        help=f"Output directory for generated archives (default: {DEFAULT_DIST_DIR})",
    )
    parser.add_argument(
        "--tgz-name",
        default=None,
        help="Optional custom .tgz archive name.",
    )
    parser.add_argument(
        "--zip-name",
        default=None,
        help="Optional custom .zip archive name.",
    )
    parser.add_argument(
        "--skip-requirements-check",
        action="store_true",
        help="Skip pre-check that requirements.txt is synchronized with uv.lock.",
    )
    args = parser.parse_args()

    try:
        tgz_path, zip_path = build_connector_archives(
            connector_dir=Path(args.connector_dir),
            output_dir=Path(args.output_dir),
            tgz_name=args.tgz_name,
            zip_name=args.zip_name,
            check_requirements=not args.skip_requirements_check,
        )
    except ValueError as e:
        raise SystemExit(str(e)) from e

    logger.info(
        f"Success: connector tgz archive generated at {tgz_path}",
        extra={"color": "green"},
    )
    logger.info(
        f"Success: connector zip archive generated at {zip_path}",
        extra={"color": "green"},
    )
    logger.info(
        "Package type detected: Connector. Upload via Content Hub > Manage > Upload > Upload Connector.",
        extra={"color": None},
    )
    logger.info(
        "Do not use Upload Solution Pack for this archive.",
        extra={"color": None},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
