import json
import tarfile
import zipfile
from pathlib import Path

import pytest

from scripts.build_connector_archives import (
    _read_connector_metadata,
    _should_skip,
    build_connector_archives,
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


def test_build_connector_archives_generate_tgz_and_zip(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    (connector_dir / "subdir").mkdir()
    (connector_dir / "subdir" / "file.txt").write_text("ok", encoding="utf-8")
    (connector_dir / "__pycache__").mkdir()
    (connector_dir / "__pycache__" / "x.pyc").write_text("x", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    tgz_archive, zip_archive = build_connector_archives(
        connector_dir=connector_dir,
        output_dir=dist_dir,
        tgz_name=None,
        zip_name=None,
        check_requirements=True,
    )

    assert tgz_archive.exists()
    with tarfile.open(tgz_archive, "r:gz") as tar:
        names = tar.getnames()

    assert "sekoia-io-xdr/info.json" in names
    assert "sekoia-io-xdr/subdir/file.txt" in names
    assert all("__pycache__" not in name for name in names)

    assert zip_archive.exists()
    with zipfile.ZipFile(zip_archive, "r") as zf:
        zip_names = zf.namelist()

    assert "sekoia-io-xdr/info.json" in zip_names
    assert "sekoia-io-xdr/subdir/file.txt" in zip_names
    assert all("__pycache__" not in name for name in zip_names)


def test_build_connector_archives_fail_when_requirements_not_synced(
    monkeypatch, tmp_path
):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 1,
    )

    with pytest.raises(RuntimeError, match="requirements.txt is not synchronized"):
        build_connector_archives(
            connector_dir=connector_dir,
            output_dir=dist_dir,
            tgz_name="x.tgz",
            zip_name="x.zip",
            check_requirements=True,
        )


def test_build_connector_archives_with_custom_names(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    (connector_dir / "subdir").mkdir()
    (connector_dir / "subdir" / "file.txt").write_text("ok", encoding="utf-8")
    (connector_dir / "__pycache__").mkdir()
    (connector_dir / "__pycache__" / "x.pyc").write_text("x", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    tgz_archive, zip_archive = build_connector_archives(
        connector_dir=connector_dir,
        output_dir=dist_dir,
        tgz_name="connector-custom.tgz",
        zip_name="connector-custom.zip",
        check_requirements=True,
    )

    assert tgz_archive.name == "connector-custom.tgz"
    assert zip_archive.name == "connector-custom.zip"


def test_build_connector_archives_reject_invalid_tgz_name(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    with pytest.raises(ValueError, match=".tgz"):
        build_connector_archives(
            connector_dir=connector_dir,
            output_dir=dist_dir,
            tgz_name="bad-name.zip",
            zip_name="ok.zip",
            check_requirements=True,
        )


def test_build_connector_archives_reject_invalid_zip_name(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    with pytest.raises(ValueError, match=".zip"):
        build_connector_archives(
            connector_dir=connector_dir,
            output_dir=dist_dir,
            tgz_name="ok.tgz",
            zip_name="bad-name.tgz",
            check_requirements=True,
        )
