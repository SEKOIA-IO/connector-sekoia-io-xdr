from connectors.core.connector import ConnectorError, get_logger

from ..constants import ASSETS_V2_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def get_asset(config, params: dict):
    """
    Retrieve a specific asset
    """
    url = f"{ASSETS_V2_BASE_URL}/{params['asset_uuid']}"
    payload = {
        "with_telemetry": params.get("with_telemetry", False),
        "with_compliance": params.get("with_compliance", False),
    }

    try:
        response = GenericAPIAction(config, "GET", url, params=payload).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
