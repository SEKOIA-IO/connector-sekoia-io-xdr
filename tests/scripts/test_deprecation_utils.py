from scripts.utils.deprecation_utils import (
    find_operation,
    find_parameter,
    normalize_deprecated_title,
    strip_deprecated_title_prefix,
)


def test_normalize_deprecated_title_uses_fallback_when_title_is_empty():
    assert (
        normalize_deprecated_title("   ", "legacy_name") == "[Deprecated] legacy_name"
    )


def test_strip_deprecated_title_prefix_variants():
    assert strip_deprecated_title_prefix("[Deprecated] Name") == "Name"
    assert strip_deprecated_title_prefix("(deprecated) Name") == "Name"
    assert strip_deprecated_title_prefix("deprecated: Name") == "Name"


def test_find_operation_and_parameter_helpers():
    data = {
        "operations": [
            {
                "operation": "op_1",
                "parameters": [{"name": "p1"}],
            }
        ]
    }

    operation = find_operation(data, "op_1")
    assert operation is not None
    assert find_parameter(operation, "p1") == {"name": "p1"}
    assert find_parameter(operation, "missing") is None
