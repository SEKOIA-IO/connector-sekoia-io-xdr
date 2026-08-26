import pytest

from scripts.deprecate_operation_parameter import (
    deprecate_operation_parameter,
    deprecate_parameter_in_file,
)


def test_deprecate_operation_parameter_with_replacement():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "status_uuid",
                        "title": "Status UUID",
                        "description": "legacy",
                    },
                    {
                        "name": "match[status_uuid]",
                        "title": "Match Status UUID",
                        "description": "canonical",
                    },
                ],
            }
        ]
    }

    changed = deprecate_operation_parameter(
        data,
        operation_name="list_alerts",
        parameter_name="status_uuid",
        replacement="match[status_uuid]",
    )

    assert changed is True
    parameter = data["operations"][0]["parameters"][0]
    assert (
        parameter["description"]
        == "Deprecated parameter. Use match[status_uuid] parameter instead."
    )
    assert parameter["title"] == "[Deprecated] Status UUID"


def test_deprecate_operation_parameter_without_replacement_uses_alias_wording():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "legacy",
                        "title": "(deprecated) Legacy Field",
                        "description": "deprecated old input",
                    }
                ],
            }
        ]
    }

    changed = deprecate_operation_parameter(
        data,
        operation_name="list_alerts",
        parameter_name="legacy",
        replacement=None,
    )

    assert changed is True
    parameter = data["operations"][0]["parameters"][0]
    assert parameter["description"] == "Deprecated alias. There is no replacement."
    assert parameter["title"] == "[Deprecated] Legacy Field"


def test_deprecate_parameter_in_file_check_then_write_then_check(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        """
{
    "operations": [
        {
            "operation": "list_alerts",
            "parameters": [
                {
                    "name": "status_uuid",
                    "title": "Status UUID",
                    "description": "legacy"
                },
                {
                    "name": "match[status_uuid]",
                    "title": "Match Status UUID",
                    "description": "canonical"
                }
            ]
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    check_before = deprecate_parameter_in_file(
        file_path,
        operation_name="list_alerts",
        parameter_name="status_uuid",
        replacement="match[status_uuid]",
        check_only=True,
    )
    write_exit = deprecate_parameter_in_file(
        file_path,
        operation_name="list_alerts",
        parameter_name="status_uuid",
        replacement="match[status_uuid]",
        check_only=False,
    )
    check_after = deprecate_parameter_in_file(
        file_path,
        operation_name="list_alerts",
        parameter_name="status_uuid",
        replacement="match[status_uuid]",
        check_only=True,
    )

    assert check_before == 1
    assert write_exit == 0
    assert check_after == 0


def test_deprecate_operation_parameter_raises_when_replacement_parameter_not_found():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "status_uuid",
                        "title": "Status UUID",
                        "description": "legacy",
                    }
                ],
            }
        ]
    }

    try:
        deprecate_operation_parameter(
            data,
            operation_name="list_alerts",
            parameter_name="status_uuid",
            replacement="match[status_uuid]",
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "Replacement parameter 'match[status_uuid]' not found in operation 'list_alerts'"
        )
    else:
        raise AssertionError("Expected ValueError for unknown replacement parameter")


def test_deprecate_operation_parameter_raises_when_replacement_operation_not_found():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "status_uuid",
                        "title": "Status UUID",
                        "description": "legacy",
                    }
                ],
            }
        ]
    }

    try:
        deprecate_operation_parameter(
            data,
            operation_name="list_alerts",
            parameter_name="status_uuid",
            replacement="other_operation.match[status_uuid]",
        )
    except ValueError as exc:
        assert str(exc) == "Replacement operation not found: other_operation"
    else:
        raise AssertionError("Expected ValueError for unknown replacement operation")


def test_deprecate_operation_parameter_raises_when_operation_not_found():
    data = {"operations": []}

    try:
        deprecate_operation_parameter(
            data,
            operation_name="missing",
            parameter_name="status_uuid",
            replacement=None,
        )
    except ValueError as exc:
        assert str(exc) == "Operation not found: missing"
    else:
        raise AssertionError("Expected ValueError for unknown operation")


def test_deprecate_operation_parameter_raises_when_parameter_not_found():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [],
            }
        ]
    }

    try:
        deprecate_operation_parameter(
            data,
            operation_name="list_alerts",
            parameter_name="missing",
            replacement=None,
        )
    except ValueError as exc:
        assert str(exc) == "Parameter 'missing' not found in operation 'list_alerts'"
    else:
        raise AssertionError("Expected ValueError for unknown parameter")


def test_deprecate_operation_parameter_raises_on_invalid_replacement_reference():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "status_uuid",
                        "title": "Status UUID",
                        "description": "legacy",
                    }
                ],
            }
        ]
    }

    try:
        deprecate_operation_parameter(
            data,
            operation_name="list_alerts",
            parameter_name="status_uuid",
            replacement="list_alerts.",
        )
    except ValueError as exc:
        assert "Replacement parameter reference must be" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid replacement reference")


def test_deprecate_parameter_in_file_already_normalized_returns_success(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        """
{
    "operations": [
        {
            "operation": "list_alerts",
            "parameters": [
                {
                    "name": "legacy",
                    "title": "[Deprecated] Legacy",
                    "description": "Deprecated alias. There is no replacement."
                }
            ]
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    assert (
        deprecate_parameter_in_file(
            file_path,
            operation_name="list_alerts",
            parameter_name="legacy",
            replacement=None,
            check_only=False,
        )
        == 0
    )


def test_deprecate_operation_parameter_raises_when_replacement_is_blank():
    data = {
        "operations": [
            {
                "operation": "list_alerts",
                "parameters": [
                    {
                        "name": "status_uuid",
                        "title": "Status UUID",
                        "description": "legacy",
                    }
                ],
            }
        ]
    }

    with pytest.raises(ValueError, match="Replacement parameter cannot be empty"):
        deprecate_operation_parameter(
            data,
            operation_name="list_alerts",
            parameter_name="status_uuid",
            replacement="   ",
        )
