import json
from pathlib import Path

from scripts.sort_info_json import build_sorted_content, sort_info_json

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "scripts"


def _fixture_text(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _fixture_json(name: str) -> dict:
    return json.loads(_fixture_text(name))


def test_build_sorted_content_matches_expected_fixture():
    result = build_sorted_content(_fixture_text("sort_info_input.json"))
    assert json.loads(result) == _fixture_json("sort_info_expected.json")


def test_sort_info_json_check_only_fails_without_writing(tmp_path):
    file_path = tmp_path / "info.json"
    original = _fixture_text("sort_info_input.json")
    file_path.write_text(original, encoding="utf-8")

    exit_code = sort_info_json(file_path, check_only=True)

    assert exit_code == 1
    assert file_path.read_text(encoding="utf-8") == original


def test_sort_info_json_write_then_check_passes(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(_fixture_text("sort_info_input.json"), encoding="utf-8")

    write_exit_code = sort_info_json(file_path, check_only=False)
    check_exit_code = sort_info_json(file_path, check_only=True)

    assert write_exit_code == 0
    assert check_exit_code == 0
    assert json.loads(file_path.read_text(encoding="utf-8")) == _fixture_json(
        "sort_info_expected.json"
    )
