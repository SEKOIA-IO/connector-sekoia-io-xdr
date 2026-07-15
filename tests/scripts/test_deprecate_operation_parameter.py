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
                    }
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
