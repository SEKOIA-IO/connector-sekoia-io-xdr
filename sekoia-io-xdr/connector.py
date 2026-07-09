from connectors.core.connector import Connector, get_logger

from .alerts.add_comment_to_alert import add_comment_to_alert
from .alerts.get_alert import get_alert
from .alerts.list_alerts import list_alerts
from .alerts.update_alert_status import update_alert_status
from .assets.delete_asset import delete_asset
from .assets.get_asset import get_asset
from .assets.update_asset import update_asset
from .cases.get_case import get_case
from .cases.search_cases import search_cases
from .countermeasures.activate_countermeasure import activate_countermeasure
from .countermeasures.deny_countermeasure import deny_countermeasure
from .events.get_events import get_events
from .health_check import check

logger = get_logger("sekoia-io-xdr")


class Sekoiaio(Connector):
    def execute(self, config, operation, params, **kwargs):
        supported_operations = {
            "activate_countermeasure": activate_countermeasure,
            "add_comment_to_alert": add_comment_to_alert,
            "delete_asset": delete_asset,
            "deny_countermeasure": deny_countermeasure,
            "get_alert": get_alert,
            "get_asset": get_asset,
            "get_case": get_case,
            "get_events": get_events,
            "list_alerts": list_alerts,
            "search_cases": search_cases,
            "update_alert_status": update_alert_status,
            "update_asset": update_asset,
        }
        return supported_operations[operation](config, params)

    def check_health(self, config):
        return check(config)
