from typing import Optional

from pydantic import AliasChoices, Field

from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class UpdateAlertStatusParams(InputModel):
    action_uuid: str
    uuid: str = Field(validation_alias=AliasChoices("uuid", "alert_uuid"))
    comment: Optional[str] = None


class UpdateAlertStatusOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = UpdateAlertStatusParams
    deprecated_aliases = DeprecatedAliases(single={"uuid": "alert_uuid"})

    def build_endpoint(self, parsed_input: UpdateAlertStatusParams) -> str:
        return f"{ALERTS_V1_BASE_URL}/{parsed_input.uuid}/workflow"

    def build_payload(self, parsed_input: UpdateAlertStatusParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "action_uuid": self.payload_value(params, "action_uuid"),
            "comment": self.payload_value(params, "comment"),
        }


def update_alert_status(config, params):
    """
    Performs an action on the alert and changes the status of the alert
    according to the performed action and the workflow.
    """
    return UpdateAlertStatusOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
