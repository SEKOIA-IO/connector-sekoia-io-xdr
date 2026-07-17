from connectors.core.connector import Connector, get_logger

from .health_check import check
from .operations.alerts.add_comment_to_alert import add_comment_to_alert
from .operations.alerts.get_alert import get_alert
from .operations.alerts.list_alerts import list_alerts
from .operations.alerts.update_alert_status import update_alert_status
from .operations.assets.delete_asset import delete_asset
from .operations.assets.get_asset import get_asset
from .operations.assets.list_assets import list_assets
from .operations.assets.revoke_assetv2 import revoke_assetv2
from .operations.assets.update_asset import update_asset
from .operations.assets.update_assets import update_assets
from .operations.cases.edit_case import edit_case
from .operations.cases.get_case import get_case
from .operations.cases.search_cases import search_cases
from .operations.countermeasures.activate_countermeasure import activate_countermeasure
from .operations.countermeasures.deny_countermeasure import deny_countermeasure
from .operations.custom_fields.get_custom_priority import get_custom_priority
from .operations.events.get_events import get_events

logger = get_logger("sekoia-io-xdr")


class Sekoiaio(Connector):
    def execute(self, config, operation, params, **kwargs):
        supported_operations = {
            "activate_countermeasure": activate_countermeasure,
            "add_comment_to_alert": add_comment_to_alert,
            "delete_asset": delete_asset,
            "deny_countermeasure": deny_countermeasure,
            "edit_case": edit_case,
            "get_alert": get_alert,
            "get_asset": get_asset,
            "get_case": get_case,
            "get_custom_priority": get_custom_priority,
            "get_events": get_events,
            "list_alerts": list_alerts,
            "list_assets": list_assets,
            "revoke_assetv2": revoke_assetv2,
            "search_cases": search_cases,
            "update_alert_status": update_alert_status,
            "update_asset": update_asset,
            "update_assets": update_assets,
        }
        return supported_operations[operation](config, params)

    def check_health(self, config):
        return check(config)
