import json
import tarfile
from pathlib import Path

import pytest

from scripts.build_connector_archive import (
    _read_connector_metadata,
    _should_skip,
    build_connector_archive,
)


def _create_minimal_connector(connector_dir: Path) -> None:
    connector_dir.mkdir(parents=True)
    (connector_dir / "images").mkdir()
    (connector_dir / "playbooks").mkdir()
    (connector_dir / "connector.py").write_text("", encoding="utf-8")
    (connector_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (connector_dir / "images" / "small.png").write_text("x", encoding="utf-8")
    payload = {"name": connector_dir.name, "version": "1.2.3"}
    (connector_dir / "info.json").write_text(json.dumps(payload), encoding="utf-8")


def test_read_connector_metadata_valid(tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    _create_minimal_connector(connector_dir)

    name, version = _read_connector_metadata(connector_dir)
    assert name == "sekoia-io-xdr"
    assert version == "1.2.3"


def test_read_connector_metadata_missing_info(tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    connector_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        _read_connector_metadata(connector_dir)


def test_read_connector_metadata_name_mismatch(tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    _create_minimal_connector(connector_dir)
    (connector_dir / "info.json").write_text(
        json.dumps({"name": "other", "version": "1.2.3"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must match info.json name"):
        _read_connector_metadata(connector_dir)


def test_read_connector_metadata_missing_name(tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    _create_minimal_connector(connector_dir)
    (connector_dir / "info.json").write_text(
        json.dumps({"version": "1.2.3"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing 'name'"):
        _read_connector_metadata(connector_dir)


def test_read_connector_metadata_missing_version(tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    _create_minimal_connector(connector_dir)
    (connector_dir / "info.json").write_text(
        json.dumps({"name": "sekoia-io-xdr"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing 'version'"):
        _read_connector_metadata(connector_dir)


def test_should_skip_filters_cache_and_pyc():
    assert _should_skip(Path("a/__pycache__/x.py"))
    assert _should_skip(Path("a/file.pyc"))
    assert not _should_skip(Path("a/file.py"))


def test_build_connector_archive_generates_tgz(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    (connector_dir / "subdir").mkdir()
    (connector_dir / "subdir" / "file.txt").write_text("ok", encoding="utf-8")
    (connector_dir / "__pycache__").mkdir()
    (connector_dir / "__pycache__" / "x.pyc").write_text("x", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.build_connector_archive.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    archive = build_connector_archive(
        connector_dir=connector_dir,
        output_dir=dist_dir,
        archive_name=None,
        check_requirements=True,
    )

    assert archive.exists()
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()

    assert "sekoia-io-xdr/info.json" in names
    assert "sekoia-io-xdr/subdir/file.txt" in names
    assert all("__pycache__" not in name for name in names)


def test_build_connector_archive_fails_when_requirements_not_synced(
    monkeypatch, tmp_path
):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    monkeypatch.setattr(
        "scripts.build_connector_archive.sync_requirements_txt",
        lambda *_args, **_kwargs: 1,
    )

    with pytest.raises(RuntimeError, match="requirements.txt is not synchronized"):
        build_connector_archive(
            connector_dir=connector_dir,
            output_dir=dist_dir,
            archive_name="x.tgz",
            check_requirements=True,
        )
