#!/usr/bin/env python3
"""Build FortiSOAR connector archives (.tgz and .zip) from the packaging directory."""

from __future__ import annotations

import argparse
import json
import subprocess
import tarfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

from scripts.sync_requirements_txt import sync_requirements_txt
from scripts.utils.cli_utils import configure_script_logger

DEFAULT_CONNECTOR_DIR = Path(".")
DEFAULT_DIST_DIR = Path("dist")
FORCED_EXCLUDED_PARTS = {
    ".git",
    ".gitignore",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tmp",
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

    return name, version


def _is_git_ignored(path: Path, repo_root: Path) -> bool:
    try:
        relative = path.relative_to(repo_root)
    except ValueError:
        return False

    proc = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-q", str(relative)],
        check=False,
        capture_output=True,
    )
    return proc.returncode == 0


def _collect_git_ignored_relpaths(
    relative_paths: Iterable[Path], repo_root: Path
) -> set[Path]:
    candidates = sorted({p.as_posix() for p in relative_paths if p != Path(".")})
    if not candidates:
        return set()

    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "check-ignore", "--stdin", "-z"],
            input="\0".join(candidates).encode("utf-8") + b"\0",
            check=False,
            capture_output=True,
        )
    except OSError:
        return set()

    if proc.returncode not in {0, 1}:
        return set()

    ignored_raw = proc.stdout.decode("utf-8", errors="ignore").split("\0")
    return {Path(item) for item in ignored_raw if item}


def _should_skip(path: Path, repo_root: Path) -> bool:
    if any(part in FORCED_EXCLUDED_PARTS for part in path.parts):
        return True
    if path.name.endswith(".pyc"):
        return True
    if _is_git_ignored(path, repo_root):
        return True
    return False


def _iter_package_paths(connector_dir: Path):
    if connector_dir.exists():
        yield connector_dir
        for path in sorted(connector_dir.rglob("*")):
            yield path


def _iter_package_files(connector_dir: Path) -> list[Path]:
    repo_root = connector_dir.resolve()
    all_files = [path for path in sorted(connector_dir.rglob("*")) if path.is_file()]
    pre_filtered_files = [
        path
        for path in all_files
        if not any(part in FORCED_EXCLUDED_PARTS for part in path.parts)
        and not path.name.endswith(".pyc")
    ]

    relative_candidates = [path.relative_to(repo_root) for path in pre_filtered_files]
    ignored_relpaths = _collect_git_ignored_relpaths(relative_candidates, repo_root)

    return [
        path
        for path in pre_filtered_files
        if path.relative_to(repo_root) not in ignored_relpaths
    ]


def _build_tgz_archive(
    repo_root: Path,
    package_files: list[Path],
    output_dir: Path,
    connector_name: str,
    archive_name: str,
    include_parent_dir: bool,
) -> Path:
    archive_path = output_dir / archive_name

    with tarfile.open(archive_path, mode="w:gz") as tar:
        for path in package_files:
            relative = path.relative_to(repo_root)
            if include_parent_dir:
                arcname = str(Path(connector_name) / relative)
            else:
                arcname = str(relative)
            tar.add(path, arcname=arcname, recursive=False)

    return archive_path


def _build_zip_archive(
    repo_root: Path,
    package_files: list[Path],
    output_dir: Path,
    connector_name: str,
    archive_name: str,
    include_parent_dir: bool,
) -> Path:
    archive_path = output_dir / archive_name

    with zipfile.ZipFile(
        archive_path, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for path in package_files:
            relative = path.relative_to(repo_root)
            if include_parent_dir:
                arcname = str(Path(connector_name) / relative)
            else:
                arcname = str(relative)
            zf.write(path, arcname=arcname)

    return archive_path


def build_connector_archives(
    connector_dir: Path,
    output_dir: Path,
    tgz_name: str | None,
    zip_name: str | None,
    check_requirements: bool,
    include_parent_dir: bool = True,
) -> tuple[Path, Path]:
    connector_dir = connector_dir.resolve()
    package_files = _iter_package_files(connector_dir)

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

    repo_root = connector_dir.resolve()
    tgz_path = _build_tgz_archive(
        repo_root,
        package_files,
        output_dir,
        connector_name,
        final_tgz_name,
        include_parent_dir,
    )
    zip_path = _build_zip_archive(
        repo_root,
        package_files,
        output_dir,
        connector_name,
        final_zip_name,
        include_parent_dir,
    )
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
    parser.add_argument(
        "--no-parent-dir",
        action="store_true",
        help=(
            "Package files at the archive root instead of nesting them under "
            "the connector name directory."
        ),
    )
    args = parser.parse_args()

    try:
        tgz_path, zip_path = build_connector_archives(
            connector_dir=Path(args.connector_dir),
            output_dir=Path(args.output_dir),
            tgz_name=args.tgz_name,
            zip_name=args.zip_name,
            check_requirements=not args.skip_requirements_check,
            include_parent_dir=not args.no_parent_dir,
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
