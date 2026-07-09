from connectors.core.connector import ConnectorError, get_logger

from ..constants import CASES_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def get_case(config, params: dict):
    """
    Retrieve a specific case
    """
    url = f"{CASES_BASE_URL}/{params['uuid']}"
    payload = {}

    if params.get("community_uuid"):
        payload["community_uuid"] = params["community_uuid"]

    payload["render"] = params.get("render", False)

    try:
        response = GenericAPIAction(config, "get", url, params=payload).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response