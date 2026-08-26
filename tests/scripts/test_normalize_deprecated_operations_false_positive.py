import json

from scripts.normalize_deprecated_parameters import normalize_deprecated_parameters


def test_does_not_deprecate_operation_on_contextual_word_only():
    data = {
        "operations": [
            {
                "operation": "revoke_assetv2",
                "description": (
                    "Revoke the requested asset (soft-delete). "
                    "Replaces the deprecated Delete an asset actions."
                ),
                "title": "Revoke an Asset (V2)",
                "parameters": [],
            }
        ]
    }

    original = json.dumps(data, sort_keys=True)
    changed = normalize_deprecated_parameters(data)
    after = json.dumps(data, sort_keys=True)

    assert changed is False
    assert after == original
    assert data["operations"][0]["title"] == "Revoke an Asset (V2)"
    assert data["operations"][0]["description"].startswith("Revoke the requested")
