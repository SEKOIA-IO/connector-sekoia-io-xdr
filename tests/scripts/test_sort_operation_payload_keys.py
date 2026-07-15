from pathlib import Path

import pytest

from scripts.sort_operation_payload_keys import sort_operation_payload_keys


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
