import json
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

from ...constants import CASES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CaseSubscriber(BaseModel):
    avatar_uuid: str
    type: str


class EditCaseParams(InputModel):
    uuid: str
    title: Optional[str] = None
    description: Optional[str] = None
    status_uuid: Optional[str] = None
    status_name: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    tags: Optional[list[str]] = None
    subscribers: Optional[list[CaseSubscriber]] = None
    verdict_uuid: Optional[str] = None
    custom_status_uuid: Optional[str] = None
    custom_priority_uuid: Optional[str] = None
    verdict_analysis: Optional[str] = None
    verdict_confidence: Optional[int] = None

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        raise ValueError("Invalid `tags` format. Expected a comma-separated string.")

    @field_validator("subscribers", mode="before")
    @classmethod
    def parse_subscribers(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "Invalid `subscribers` format. Expected a JSON array."
                ) from e
            if not isinstance(parsed, list):
                raise ValueError("Invalid `subscribers` format. Expected a JSON array.")
            return parsed
        raise ValueError("Invalid `subscribers` format. Expected a JSON array.")


class EditCaseOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = EditCaseParams

    def build_endpoint(self, parsed_input: EditCaseParams) -> str:
        return f"{CASES_V1_BASE_URL}/{parsed_input.uuid}"

    def build_payload(self, parsed_input: EditCaseParams) -> dict:
        params = parsed_input.model_dump()
        payload = {
            "custom_priority_uuid": self.payload_value(params, "custom_priority_uuid"),
            "custom_status_uuid": self.payload_value(params, "custom_status_uuid"),
            "description": self.payload_value(params, "description"),
            "priority": self.payload_value(params, "priority"),
            "status_name": self.payload_value(params, "status_name"),
            "status_uuid": self.payload_value(params, "status_uuid"),
            "subscribers": self.payload_value(params, "subscribers"),
            "tags": self.payload_value(params, "tags"),
            "title": self.payload_value(params, "title"),
            "verdict_analysis": self.payload_value(params, "verdict_analysis"),
            "verdict_confidence": self.payload_value(params, "verdict_confidence"),
            "verdict_uuid": self.payload_value(params, "verdict_uuid"),
        }
        return {key: value for key, value in payload.items() if value is not None}


def edit_case(config, params: dict):
    """Edit the properties of a case."""
    return EditCaseOperation(api_action_cls=GenericAPIAction).execute(config, params)
