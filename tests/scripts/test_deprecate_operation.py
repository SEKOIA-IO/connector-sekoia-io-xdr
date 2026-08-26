from scripts.deprecate_operation import deprecate_operation, deprecate_operation_in_file


def test_deprecate_operation_with_replacement():
    data = {
        "operations": [
            {
                "operation": "delete_asset",
                "title": "Delete Asset",
                "description": "Delete an asset",
                "parameters": [],
            },
            {
                "operation": "revoke_assetv2",
                "title": "Revoke Asset",
                "description": "Revoke an asset",
                "parameters": [],
            },
        ]
    }

    changed = deprecate_operation(
        data,
        operation_name="delete_asset",
        replacement="revoke_assetv2",
    )

    assert changed is True
    operation = data["operations"][0]
    assert (
        operation["description"]
        == "Deprecated operation. Use revoke_assetv2 operation instead."
    )
    assert operation["title"] == "[Deprecated] Delete Asset"


def test_deprecate_operation_without_replacement():
    data = {
        "operations": [
            {
                "operation": "legacy_operation",
                "title": "Legacy Operation",
                "description": "deprecated old operation",
                "parameters": [],
            }
        ]
    }

    changed = deprecate_operation(
        data,
        operation_name="legacy_operation",
        replacement=None,
    )

    assert changed is True
    operation = data["operations"][0]
    assert operation["description"] == "Deprecated operation. There is no replacement."
    assert operation["title"] == "[Deprecated] Legacy Operation"


def test_deprecate_operation_in_file_check_then_write_then_check(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        """
{
    "operations": [
        {
            "operation": "delete_asset",
            "title": "Delete Asset",
            "description": "Delete an asset",
            "parameters": []
        },
        {
            "operation": "revoke_assetv2",
            "title": "Revoke Asset",
            "description": "Revoke an asset",
            "parameters": []
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    check_before = deprecate_operation_in_file(
        file_path,
        operation_name="delete_asset",
        replacement="revoke_assetv2",
        check_only=True,
    )
    write_exit = deprecate_operation_in_file(
        file_path,
        operation_name="delete_asset",
        replacement="revoke_assetv2",
        check_only=False,
    )
    check_after = deprecate_operation_in_file(
        file_path,
        operation_name="delete_asset",
        replacement="revoke_assetv2",
        check_only=True,
    )

    assert check_before == 1
    assert write_exit == 0
    assert check_after == 0


def test_deprecate_operation_raises_when_replacement_operation_not_found():
    data = {
        "operations": [
            {
                "operation": "delete_asset",
                "title": "Delete Asset",
                "description": "Delete an asset",
                "parameters": [],
            }
        ]
    }

    try:
        deprecate_operation(
            data,
            operation_name="delete_asset",
            replacement="missing_operation",
        )
    except ValueError as exc:
        assert str(exc) == "Replacement operation not found: missing_operation"
    else:
        raise AssertionError("Expected ValueError for unknown replacement operation")


def test_deprecate_operation_raises_when_operation_not_found():
    data = {"operations": []}

    try:
        deprecate_operation(data, operation_name="missing", replacement=None)
    except ValueError as exc:
        assert str(exc) == "Operation not found: missing"
    else:
        raise AssertionError("Expected ValueError for unknown operation")


def test_deprecate_operation_raises_when_replacement_is_blank():
    data = {
        "operations": [
            {
                "operation": "delete_asset",
                "title": "Delete Asset",
                "description": "Delete an asset",
                "parameters": [],
            }
        ]
    }

    try:
        deprecate_operation(data, operation_name="delete_asset", replacement="   ")
    except ValueError as exc:
        assert str(exc) == "Replacement operation cannot be empty"
    else:
        raise AssertionError("Expected ValueError for blank replacement")


def test_deprecate_operation_in_file_already_normalized_returns_success(tmp_path):
    file_path = tmp_path / "info.json"
    file_path.write_text(
        """
{
    "operations": [
        {
            "operation": "delete_asset",
            "title": "[Deprecated] Delete Asset",
            "description": "Deprecated operation. There is no replacement.",
            "parameters": []
        }
    ]
}
""".strip() + "\n",
        encoding="utf-8",
    )

    assert (
        deprecate_operation_in_file(
            file_path,
            operation_name="delete_asset",
            replacement=None,
            check_only=False,
        )
        == 0
    )
