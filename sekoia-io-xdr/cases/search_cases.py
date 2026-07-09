from connectors.core.connector import ConnectorError, get_logger

from ..constants import CASES_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def search_cases(config, params: dict):
    """
    Search cases filtered by optional query parameters
    """
    payload: dict = {
        "match[community_uuid]": params.get("community_uuid"),
        "match[status_uuid]": params.get("status_uuid"),
        "match[status_name]": params.get("status_name"),
        "date[created_at]": params.get("created_at"),
        "match[created_by]": params.get("created_by"),
        "match[tags]": params.get("tags"),
        "match[assignees]": params.get("assignees"),
        "limit": params.get("limit") or 20,
        "offset": params.get("offset") or 0,
        "sort": params.get("sort"),
        "direction": params.get("direction"),
    }

    try:
        response: dict = GenericAPIAction(
            config, "get", CASES_BASE_URL, params=payload
        ).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
