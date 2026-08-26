import json
import tarfile
import zipfile
from pathlib import Path

import pytest

from scripts.build_connector_archives import (
    _collect_git_ignored_relpaths,
    _is_git_ignored,
    _iter_package_paths,
    _read_connector_metadata,
    _should_skip,
    build_connector_archives,
)


def _create_minimal_connector(connector_dir: Path) -> None:
    connector_dir.mkdir(parents=True, exist_ok=True)
    (connector_dir / "images").mkdir()
    (connector_dir / "playbooks").mkdir()
    (connector_dir / "connector.py").write_text("", encoding="utf-8")
    (connector_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (connector_dir / "images" / "small.png").write_text("x", encoding="utf-8")
    payload = {"name": "sekoia-io-xdr", "version": "1.2.3"}
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
    connector_dir = tmp_path / "repo-root"
    _create_minimal_connector(connector_dir)
    (connector_dir / "info.json").write_text(
        json.dumps({"name": "other", "version": "1.2.3"}),
        encoding="utf-8",
    )

    name, version = _read_connector_metadata(connector_dir)
    assert name == "other"
    assert version == "1.2.3"


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


def test_should_skip_filters_cache_and_pyc(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    assert _should_skip(repo_root / "a" / "__pycache__" / "x.py", repo_root)
    assert _should_skip(repo_root / "a" / "file.pyc", repo_root)
    assert not _should_skip(repo_root / "a" / "file.py", repo_root)


def test_should_skip_when_git_ignored(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    candidate = repo_root / "ignored.txt"
    monkeypatch.setattr(
        "scripts.build_connector_archives._is_git_ignored", lambda *_args: True
    )
    assert _should_skip(candidate, repo_root)


def test_is_git_ignored_outside_repo_root_returns_false(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside = tmp_path / "outside.txt"
    assert _is_git_ignored(outside, repo_root) is False


def test_collect_git_ignored_relpaths_empty_input_returns_empty_set(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    assert _collect_git_ignored_relpaths([], repo_root) == set()


def test_collect_git_ignored_relpaths_oserror_returns_empty_set(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    def _raise_oserror(*_args, **_kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(
        "scripts.build_connector_archives.subprocess.run", _raise_oserror
    )
    result = _collect_git_ignored_relpaths([Path("a.txt")], repo_root)
    assert result == set()


def test_collect_git_ignored_relpaths_parses_git_stdout(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    class Proc:
        returncode = 0
        stdout = b"a.txt\0nested/b.txt\0"

    monkeypatch.setattr(
        "scripts.build_connector_archives.subprocess.run",
        lambda *_args, **_kwargs: Proc(),
    )

    result = _collect_git_ignored_relpaths(
        [Path("a.txt"), Path("nested/b.txt")], repo_root
    )
    assert result == {Path("a.txt"), Path("nested/b.txt")}


def test_iter_package_paths_yields_root_and_nested_paths(tmp_path):
    connector_dir = tmp_path / "connector"
    (connector_dir / "sub").mkdir(parents=True)
    (connector_dir / "sub" / "f.txt").write_text("x", encoding="utf-8")

    paths = list(_iter_package_paths(connector_dir))
    assert connector_dir in paths
    assert (connector_dir / "sub") in paths
    assert (connector_dir / "sub" / "f.txt") in paths


def test_build_connector_archives_generate_tgz_and_zip(monkeypatch, tmp_path):
    connector_dir = tmp_path / "repo-root"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)
    (connector_dir / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (connector_dir / "README.md").write_text("# Readme\n", encoding="utf-8")
    (connector_dir / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    (connector_dir / "tests").mkdir()
    (connector_dir / "tests" / "test_dummy.py").write_text("pass\n", encoding="utf-8")
    (connector_dir / "scripts").mkdir()
    (connector_dir / "scripts" / "build.py").write_text("pass\n", encoding="utf-8")
    (connector_dir / ".github").mkdir()
    (connector_dir / ".github" / "workflows.yml").write_text("x\n", encoding="utf-8")

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
    assert "sekoia-io-xdr/CHANGELOG.md" in names
    assert "sekoia-io-xdr/README.md" in names
    assert "sekoia-io-xdr/tests/test_dummy.py" in names
    assert "sekoia-io-xdr/scripts/build.py" in names
    assert "sekoia-io-xdr/.gitignore" not in names
    assert all("/.github/" not in name for name in names)
    assert all("__pycache__" not in name for name in names)

    assert zip_archive.exists()
    with zipfile.ZipFile(zip_archive, "r") as zf:
        zip_names = zf.namelist()

    assert "sekoia-io-xdr/info.json" in zip_names
    assert "sekoia-io-xdr/subdir/file.txt" in zip_names
    assert "sekoia-io-xdr/CHANGELOG.md" in zip_names
    assert "sekoia-io-xdr/README.md" in zip_names
    assert "sekoia-io-xdr/tests/test_dummy.py" in zip_names
    assert "sekoia-io-xdr/scripts/build.py" in zip_names
    assert "sekoia-io-xdr/.gitignore" not in zip_names
    assert all("/.github/" not in name for name in zip_names)
    assert all("__pycache__" not in name for name in zip_names)


def test_build_connector_archives_fail_when_requirements_not_synced(
    monkeypatch, tmp_path
):
    connector_dir = tmp_path / "repo-root"
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
    connector_dir = tmp_path / "repo-root"
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


def test_build_connector_archives_without_parent_dir(monkeypatch, tmp_path):
    connector_dir = tmp_path / "repo-root"
    dist_dir = tmp_path / "dist"
    _create_minimal_connector(connector_dir)
    (connector_dir / "README.md").write_text("# Readme\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.build_connector_archives.sync_requirements_txt",
        lambda *_args, **_kwargs: 0,
    )

    tgz_archive, zip_archive = build_connector_archives(
        connector_dir=connector_dir,
        output_dir=dist_dir,
        tgz_name="flat.tgz",
        zip_name="flat.zip",
        check_requirements=True,
        include_parent_dir=False,
    )

    with tarfile.open(tgz_archive, "r:gz") as tar:
        tgz_names = tar.getnames()
    assert "info.json" in tgz_names
    assert "README.md" in tgz_names
    assert "sekoia-io-xdr/info.json" not in tgz_names

    with zipfile.ZipFile(zip_archive, "r") as zf:
        zip_names = zf.namelist()
    assert "info.json" in zip_names
    assert "README.md" in zip_names
    assert "sekoia-io-xdr/info.json" not in zip_names


def test_build_connector_archives_reject_invalid_tgz_name(monkeypatch, tmp_path):
    connector_dir = tmp_path / "repo-root"
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
    connector_dir = tmp_path / "repo-root"
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
