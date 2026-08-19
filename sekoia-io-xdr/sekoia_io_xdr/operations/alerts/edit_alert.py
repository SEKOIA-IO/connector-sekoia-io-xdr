from typing import Optional

from pydantic import AliasChoices, Field

from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class EditAlertParams(InputModel):
    uuid: str = Field(validation_alias=AliasChoices("uuid", "alert_uuid"))
    alert_type_category: Optional[str] = None
    alert_type_value: Optional[str] = None
    details: Optional[str] = None
    urgency: Optional[int] = None
    kill_chain_short_id: Optional[str] = None
    title: Optional[str] = None
    status_uuid: Optional[str] = None
    comment: Optional[str] = None
    verdict_analysis: Optional[str] = None
    verdict_confidence: Optional[int] = None
    assignee: Optional[str] = None
    verdict_uuid: Optional[str] = None
    custom_status_uuid: Optional[str] = None


class EditAlertOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = EditAlertParams
    deprecated_aliases = DeprecatedAliases(single={"uuid": "alert_uuid"})

    def build_endpoint(self, parsed_input: EditAlertParams) -> str:
        return f"{ALERTS_V1_BASE_URL}/{parsed_input.uuid}"

    def build_payload(self, parsed_input: EditAlertParams) -> dict:
        params = parsed_input.model_dump()
        payload = {
            "alert_type_category": self.payload_value(params, "alert_type_category"),
            "alert_type_value": self.payload_value(params, "alert_type_value"),
            "assignee": self.payload_value(params, "assignee"),
            "comment": self.payload_value(params, "comment"),
            "custom_status_uuid": self.payload_value(params, "custom_status_uuid"),
            "details": self.payload_value(params, "details"),
            "kill_chain_short_id": self.payload_value(params, "kill_chain_short_id"),
            "status_uuid": self.payload_value(params, "status_uuid"),
            "title": self.payload_value(params, "title"),
            "urgency": self.payload_value(params, "urgency"),
            "verdict_analysis": self.payload_value(params, "verdict_analysis"),
            "verdict_confidence": self.payload_value(params, "verdict_confidence"),
            "verdict_uuid": self.payload_value(params, "verdict_uuid"),
        }
        return {key: value for key, value in payload.items() if value is not None}


def edit_alert(config, params: dict):
    """Edit the details of an alert."""
    return EditAlertOperation(api_action_cls=GenericAPIAction).execute(config, params)
