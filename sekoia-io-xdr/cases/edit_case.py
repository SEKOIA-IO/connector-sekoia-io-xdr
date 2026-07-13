import json

from connectors.core.connector import ConnectorError, get_logger

from ..constants import CASES_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def edit_case(config, params: dict):
    """
    Edit the properties of a case.
    """
    url = f"{CASES_BASE_URL}/{params['uuid']}"

    payload: dict = {}
    passthrough_fields = [
        "title",
        "description",
        "status_uuid",
        "status_name",
        "priority",
        "verdict_uuid",
        "custom_status_uuid",
        "custom_priority_uuid",
        "verdict_analysis",
        "verdict_confidence",
    ]

    for field in passthrough_fields:
        value = params.get(field)
        if value is not None:
            payload[field] = value

    tags = params.get("tags")
    if tags is not None:
        payload["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

    subscribers = params.get("subscribers")
    if subscribers is not None:
        try:
            payload["subscribers"] = json.loads(subscribers)
        except (TypeError, json.JSONDecodeError) as e:
            raise ConnectorError(
                "Error: Invalid `subscribers` format. Expected a JSON array."
            ) from e

    try:
        response = GenericAPIAction(config, "PATCH", url, json=payload).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
