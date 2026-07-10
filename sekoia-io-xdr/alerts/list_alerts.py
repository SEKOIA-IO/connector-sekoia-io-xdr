from connectors.core.connector import ConnectorError, get_logger

from ..constants import ALERTS_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def list_alerts(config, params):
    url: str = ALERTS_BASE_URL

    if params.get("creation_start_date") or params.get("creation_end_date"):
        created_at = (
            f"{params['creation_start_date'] or ''},{params['creation_end_date'] or ''}"
        )
    else:
        created_at = None

    if params.get("updated_start_date") or params.get("updated_end_date"):
        updated_at = (
            f"{params['updated_start_date'] or ''},{params['updated_end_date'] or ''}"
        )
    else:
        updated_at = None

    payload: dict = {
        "match[community_uuid]": params.get("match[community_uuid]"),
        "match[entity_name]": params.get("match[entity_name]"),
        "match[entity_uuid]": params.get("match[entity_uuid]"),
        "match[status_uuid]": params.get("match[status_uuid]")
        or params.get("status_uuid"),
        "match[status_name]": params.get("match[status_name]")
        or params.get("status_name"),
        "match[type_category]": params.get("match[type_category]"),
        "match[type_value]": params.get("match[type_value]"),
        "match[source]": params.get("match[source]"),
        "match[target]": params.get("match[target]"),
        "match[node]": params.get("match[node]"),
        "match[stix_object]": params.get("match[stix_object]"),
        "match[rule_uuid]": params.get("match[rule_uuid]") or params.get("rule_uuid"),
        "match[rule_name]": params.get("match[rule_name]") or params.get("rule_name"),
        "match[detection_type]": params.get("match[detection_type]"),
        "match[short_id]": params.get("match[short_id]") or params.get("short_id"),
        "match[uuid]": params.get("match[uuid]"),
        "match[title]": params.get("match[title]"),
        "match[asset_uuid]": params.get("match[asset_uuid]"),
        "match[urgency_display]": params.get("match[urgency_display]"),
        "match[case_short_id]": params.get("match[case_short_id]"),
        "match[assignee]": params.get("match[assignee]"),
        "match[custom_status_uuid]": params.get("match[custom_status_uuid]"),
        "match[verdict_uuid]": params.get("match[verdict_uuid]"),
        "date[created_at]": params.get("date[created_at]") or created_at,
        "date[updated_at]": params.get("date[updated_at]") or updated_at,
        "range[urgency]": params.get("range[urgency]"),
        "range[similar]": params.get("range[similar]"),
        "nomatch[asset_uuid]": params.get("nomatch[asset_uuid]"),
        "nomatch[entity_uuid]": params.get("nomatch[entity_uuid]"),
        "nomatch[rule_uuid]": params.get("nomatch[rule_uuid]"),
        "nomatch[rule_name]": params.get("nomatch[rule_name]"),
        "nomatch[detection_type]": params.get("nomatch[detection_type]"),
        "nomatch[source]": params.get("nomatch[source]"),
        "nomatch[target]": params.get("nomatch[target]"),
        "nomatch[status_uuid]": params.get("nomatch[status_uuid]"),
        "nomatch[stix_object]": params.get("nomatch[stix_object]"),
        "nomatch[type_value]": params.get("nomatch[type_value]"),
        "nomatch[urgency_display]": params.get("nomatch[urgency_display]"),
        "nomatch[assignee]": params.get("nomatch[assignee]"),
        "nomatch[custom_status_uuid]": params.get("nomatch[custom_status_uuid]"),
        "nomatch[verdict_uuid]": params.get("nomatch[verdict_uuid]"),
        "visible": params.get("visible", True),
        "is_assigned_to_case": params.get("is_assigned_to_case"),
        "similar_to": params.get("similar_to"),
        "limit": params.get("limit", 20),
        "offset": params.get("offset", 0),
        "stix": params.get("stix", False),
        "cases": params.get("cases", False),
        "sort": params.get("sort"),
        "direction": params.get("direction"),
        "with_count": params.get("with_count", True),
    }

    try:
        response: dict = GenericAPIAction(config, "get", url, params=payload).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
