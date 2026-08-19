import json
from pathlib import Path

from scripts.normalize_deprecated_parameters import (
    extract_replacement_alias,
    extract_replacement_operation,
    normalize_deprecated_parameters,
    normalize_file,
    resolve_replacement_parameter_name,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "scripts"


def _fixture_text(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _fixture_json(name: str) -> dict:
    return json.loads(_fixture_text(name))


def test_extract_replacement_alias_supports_multiple_deprecated_patterns():
    assert (
        extract_replacement_alias(
            "Deprecated parameter. Use match[status_uuid] parameter instead."
        )
        == "match[status_uuid]"
    )
    assert (
        extract_replacement_alias("Deprecated: use UUID instead. The field is legacy.")
        == "UUID"
    )
    assert extract_replacement_alias("Deprecated alias with no suggestion") is None


def test_extract_replacement_operation_supports_canonical_pattern():
    assert (
        extract_replacement_operation(
            "Deprecated operation. Use revoke_assetv2 operation instead."
        )
        == "revoke_assetv2"
    )
    assert (
        extract_replacement_operation("Deprecated operation with no suggestion") is None
    )


def test_normalize_deprecated_parameters_matches_expected_fixture():
    data = _fixture_json("deprecated_params_input.json")

    changed = normalize_deprecated_parameters(data)

    assert changed is True
    assert data == _fixture_json("deprecated_params_expected.json")


def test_normalize_deprecated_parameters_uses_replacement_name_not_title():
    data = {
        "operations": [
            {
                "operation": "add_comment_to_alert",
                "parameters": [
                    {
                        "name": "alert_uuid",
                        "title": "Alert Identifier",
                        "description": "Deprecated parameter. Use UUID parameter instead.",
                    },
                    {
                        "name": "uuid",
                        "title": "UUID",
                        "description": "Canonical uuid parameter",
                    },
                ],
            }
        ]
    }

    changed = normalize_deprecated_parameters(data)

    assert changed is True
    assert data["operations"][0]["parameters"][0]["description"] == (
        "Deprecated parameter. Use uuid parameter instead."
    )


def test_normalize_file_check_only_then_write_then_check(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        _fixture_text("deprecated_params_input.json"), encoding="utf-8"
    )

    check_before = normalize_file(file_path, check_only=True)
    write_exit = normalize_file(file_path, check_only=False)
    check_after = normalize_file(file_path, check_only=True)

    assert check_before == 1
    assert write_exit == 0
    assert check_after == 0
    assert json.loads(file_path.read_text(encoding="utf-8")) == _fixture_json(
        "deprecated_params_expected.json"
    )


def test_resolve_replacement_parameter_name_by_title_fallback():
    operation = {
        "parameters": [
            {
                "name": "uuid",
                "title": "UUID",
            }
        ]
    }

    assert resolve_replacement_parameter_name(operation, "UUID") == "uuid"


def test_resolve_replacement_parameter_name_keeps_unmapped_value():
    operation = {"parameters": []}

    assert (
        resolve_replacement_parameter_name(operation, "unknown_token")
        == "unknown_token"
    )


def test_resolve_replacement_parameter_name_returns_none_for_blank_replacement():
    operation = {"parameters": [{"name": "uuid", "title": "UUID"}]}

    assert resolve_replacement_parameter_name(operation, "   ") is None


def test_normalize_deprecated_parameters_skips_entries_without_required_names():
    data = {
        "operations": [
            {
                "operation": "",
                "title": "[Deprecated] Missing operation name",
                "description": "Deprecated operation.",
                "parameters": [
                    {
                        "name": "",
                        "title": "[Deprecated] Legacy",
                        "description": "Deprecated parameter.",
                    }
                ],
            }
        ]
    }

    assert normalize_deprecated_parameters(data) is False


def test_normalize_file_returns_success_when_already_normalized(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        _fixture_text("deprecated_params_expected.json"),
        encoding="utf-8",
    )

    assert normalize_file(file_path, check_only=False) == 0


def test_resolve_replacement_parameter_name_uses_deprecated_title_prefix_fallback():
    operation = {
        "parameters": [
            {
                "name": "uuid",
                "title": "[Deprecated] UUID",
            }
        ]
    }

    assert resolve_replacement_parameter_name(operation, "UUID") == "uuid"


def test_resolve_replacement_parameter_name_uses_title_when_name_does_not_match():
    operation = {
        "parameters": [
            {
                "name": "canonical_uuid",
                "title": "[Deprecated] UUID",
            }
        ]
    }

    assert resolve_replacement_parameter_name(operation, "UUID") == "canonical_uuid"
