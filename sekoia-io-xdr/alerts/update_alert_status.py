from connectors.core.connector import ConnectorError, get_logger

from ..constants import ALERTS_BASE_URL
from ..utils import GenericAPIAction

logger = get_logger("sekoia-io-xdr")


def update_alert_status(config, params):
    """
    Performs an action on the alert and changes the status of the alert
    according to the performed action and the workflow.
    """
    alert_uuid = params.get("uuid") or params.get("alert_uuid")
    if not alert_uuid:
        raise ConnectorError(
            "Error: Missing required parameter 'uuid' (or deprecated 'alert_uuid')."
        )

    url = f"{ALERTS_BASE_URL}/{alert_uuid}/workflow"
    body = {"action_uuid": params["action_uuid"], "comment": params.get("comment")}

    try:
        response = GenericAPIAction(config, "PATCH", url, json=body).run()
    except Exception as e:
        raise ConnectorError(f"Error: {e}")

    return response
