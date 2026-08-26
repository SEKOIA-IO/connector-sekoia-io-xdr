from pathlib import Path

import libcst as cst
import pytest

from scripts.sort_operation_payload_keys import _string_key, sort_operation_payload_keys


def _write(file_path: Path, content: str) -> None:
    file_path.write_text(content.strip() + "\n", encoding="utf-8")


def test_sort_operation_payload_keys_check_and_fix(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    file_path = tmp_path / "sample_operation.py"
    _write(
        file_path,
        """
class Demo:
    def build_payload(self, parsed_input):
        return {
            "b": 2,
            "a": 1,
        }
""",
    )

    monkeypatch.chdir(tmp_path)
    pattern = "*.py"

    check_before = sort_operation_payload_keys(check_only=True, pattern=pattern)
    write_exit = sort_operation_payload_keys(check_only=False, pattern=pattern)
    check_after = sort_operation_payload_keys(check_only=True, pattern=pattern)

    assert check_before == 1
    assert write_exit == 0
    assert check_after == 0

    content = file_path.read_text(encoding="utf-8")
    assert content.index('"a"') < content.index('"b"')


def test_sort_operation_payload_keys_ignores_non_direct_dict_return(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    file_path = tmp_path / "sample_operation.py"
    _write(
        file_path,
        """
class Demo:
    def build_payload(self, parsed_input):
        payload = {
            "b": 2,
            "a": 1,
        }
        return payload
""",
    )

    monkeypatch.chdir(tmp_path)
    pattern = "*.py"
    assert sort_operation_payload_keys(check_only=True, pattern=pattern) == 0


def test_sort_operation_payload_keys_ignores_non_string_dict_keys(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    file_path = tmp_path / "sample_operation.py"
    _write(
        file_path,
        """
class Demo:
    def build_payload(self, parsed_input):
        return {
            parsed_input.key: 2,
            "a": 1,
        }
""",
    )

    monkeypatch.chdir(tmp_path)
    pattern = "*.py"

    assert sort_operation_payload_keys(check_only=True, pattern=pattern) == 0
    assert sort_operation_payload_keys(check_only=False, pattern=pattern) == 0


def test_string_key_returns_none_when_literal_eval_fails(
    monkeypatch: pytest.MonkeyPatch,
):
    import scripts.sort_operation_payload_keys as mod

    element = cst.DictElement(
        key=cst.SimpleString(value='"a"'),
        value=cst.Integer(value="1"),
    )

    monkeypatch.setattr(
        mod.ast, "literal_eval", lambda _v: (_ for _ in ()).throw(ValueError("bad"))
    )

    assert _string_key(element) is None


def test_sort_operation_payload_keys_ignores_return_outside_build_payload(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    file_path = tmp_path / "sample_operation.py"
    _write(
        file_path,
        """
class Demo:
    def not_build_payload(self, parsed_input):
        return {
            "b": 2,
            "a": 1,
        }
""",
    )

    monkeypatch.chdir(tmp_path)
    assert sort_operation_payload_keys(check_only=True, pattern="*.py") == 0


def test_sort_operation_payload_keys_ignores_starred_dict_elements(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    file_path = tmp_path / "sample_operation.py"
    _write(
        file_path,
        """
class Demo:
    def build_payload(self, parsed_input):
        base = {"a": 1}
        return {
            **base,
            "b": 2,
        }
""",
    )

    monkeypatch.chdir(tmp_path)
    assert sort_operation_payload_keys(check_only=True, pattern="*.py") == 0


def test_sort_operation_payload_keys_skips_pycache_files(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    _write(
        cache_dir / "ignored.py",
        """
class Demo:
    def build_payload(self, parsed_input):
        return {
            "b": 2,
            "a": 1,
        }
""",
    )

    monkeypatch.chdir(tmp_path)
    assert sort_operation_payload_keys(check_only=True, pattern="**/*.py") == 0
