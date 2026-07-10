from connectors.core.connector import ConnectorError, get_logger

from ..constants import ASSETS_V2_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def list_assets(config, params: dict):
    """
    Search assets filtered by optional query parameters
    """
    payload: dict = {
        "search": params.get("search"),
        "also_search_in_detection_properties": params.get(
            "also_search_in_detection_properties", False
        ),
        "also_search_in_tags": params.get("also_search_in_tags", False),
        "uuids": params.get("uuids"),
        "community_uuids": params.get("community_uuids"),
        "type": params.get("type"),
        "category": params.get("category"),
        "source": params.get("source"),
        "tags": params.get("tags"),
        "reviewed": params.get("reviewed"),
        "criticality": params.get("criticality"),
        "sort": params.get("sort"),
        "direction": params.get("direction"),
        "with_telemetry": params.get("with_telemetry", False),
        "incorporate_atoms": params.get("incorporate_atoms", False),
        "include_revoked": params.get("include_revoked", False),
        "rule_uuid": params.get("rule_uuid"),
        "rule_version": params.get("rule_version"),
        "connectors": params.get("connectors"),
        "connectors_configuration": params.get("connectors_configuration"),
        "format": params.get("format"),
        "include_intake_formats": params.get("include_intake_formats", False),
        "intake_format_uuids": params.get("intake_format_uuids"),
        "limit": params.get("limit") or 20,
        "offset": params.get("offset") or 0,
    }

    try:
        response: dict = GenericAPIAction(
            config, "get", ASSETS_V2_BASE_URL, params=payload
        ).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
