import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _run_script(module_file: str):
    return runpy.run_path(str(SCRIPTS_DIR / module_file), run_name="__main__")


def test_build_connector_archive_main_invalid_archive_name(monkeypatch):
    from scripts import build_connector_archive as mod

    monkeypatch.setattr(
        sys,
        "argv",
        ["build_connector_archive.py", "--archive-name", "bad-name.zip"],
    )

    with pytest.raises(SystemExit, match="must end with .tgz"):
        mod.main()


def test_build_connector_archive_main_success(monkeypatch, tmp_path):
    from scripts import build_connector_archive as mod

    output_dir = tmp_path / "out"
    expected = output_dir / "archive.tgz"

    monkeypatch.setattr(
        mod,
        "build_connector_archive",
        lambda **_kwargs: expected,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["build_connector_archive.py", "--output-dir", str(output_dir)],
    )

    assert mod.main() == 0


def test_sync_requirements_txt_entrypoint_check(monkeypatch):
    class _Completed:
        def __init__(self, stdout: str):
            self.stdout = stdout

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: _Completed(stdout="expected\n"),
    )

    req_file = Path("/tmp/req-check.txt")
    req_file.write_text("expected\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["sync_requirements_txt.py", str(req_file), "--check"],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("sync_requirements_txt.py")

    assert exc.value.code == 0


def test_build_connector_archive_entrypoint_module(monkeypatch, tmp_path):
    connector_dir = tmp_path / "sekoia-io-xdr"
    connector_dir.mkdir()
    (connector_dir / "info.json").write_text(
        '{"name":"sekoia-io-xdr","version":"1.0.0"}',
        encoding="utf-8",
    )
    (connector_dir / "requirements.txt").write_text("requests\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_connector_archive.py",
            "--connector-dir",
            str(connector_dir),
            "--output-dir",
            str(tmp_path / "dist"),
            "--skip-requirements-check",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("build_connector_archive.py")

    assert exc.value.code == 0


def test_deprecate_operation_entrypoint(monkeypatch, tmp_path):
    info = tmp_path / "info.json"
    info.write_text(
        """
{
    "operations": [
        {
            "operation": "old_op",
            "title": "Old Op",
            "description": "legacy",
            "parameters": []
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["deprecate_operation.py", "old_op", "--path", str(info)],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("deprecate_operation.py")

    assert exc.value.code == 0


def test_deprecate_operation_parameter_entrypoint(monkeypatch, tmp_path):
    info = tmp_path / "info.json"
    info.write_text(
        """
{
    "operations": [
        {
            "operation": "op",
            "parameters": [
                {"name": "legacy", "title": "Legacy", "description": "old"}
            ]
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["deprecate_operation_parameter.py", "op", "legacy", "--path", str(info)],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("deprecate_operation_parameter.py")

    assert exc.value.code == 0


def test_normalize_deprecated_parameters_entrypoint_check(monkeypatch, tmp_path):
    info = tmp_path / "info.json"
    info.write_text(
        """
{
    "operations": [
        {
            "operation": "op",
            "title": "(deprecated) op",
            "description": "Deprecated operation. There is no replacement.",
            "parameters": []
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["normalize_deprecated_parameters.py", str(info), "--check"],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("normalize_deprecated_parameters.py")

    assert exc.value.code in {0, 1}


def test_sort_info_json_entrypoint_check(monkeypatch, tmp_path):
    info = tmp_path / "info.json"
    info.write_text('{"b": 1, "a": 2}\n', encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["sort_info_json.py", str(info), "--check"])

    with pytest.raises(SystemExit) as exc:
        _run_script("sort_info_json.py")

    assert exc.value.code == 1


def test_sort_operation_payload_keys_entrypoint(monkeypatch, tmp_path):
    target = tmp_path / "sample.py"
    target.write_text(
        """
class Demo:
    def build_payload(self, parsed_input):
        return {"b": 2, "a": 1}
""".strip() + "\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["sort_operation_payload_keys.py", "--check", "--pattern", "*.py"],
    )

    with pytest.raises(SystemExit) as exc:
        _run_script("sort_operation_payload_keys.py")

    assert exc.value.code == 1
