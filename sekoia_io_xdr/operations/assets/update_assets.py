import json
from typing import Literal, Optional

from pydantic import field_validator

from ...constants import ASSETS_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class UpdateAssetsParams(InputModel):
    uuid: str
    entity_uuid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Literal["host", "account", "network"]] = None
    category: Optional[str] = None
    criticality: Optional[int] = None
    props: Optional[dict] = None
    atoms: Optional[dict] = None
    tags: Optional[list[str]] = None
    reviewed: Optional[bool] = None
    revoked: Optional[bool] = None

    @field_validator("props", "atoms", mode="before")
    @classmethod
    def parse_json_object_fields(cls, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError("Expected a JSON object.") from e
            if not isinstance(parsed, dict):
                raise ValueError("Expected a JSON object.")
            return parsed
        raise ValueError("Expected a JSON object.")

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        "Invalid `tags` format. Expected a comma-separated string or JSON array."
                    ) from e
                if not isinstance(parsed, list) or not all(
                    isinstance(item, str) for item in parsed
                ):
                    raise ValueError(
                        "Invalid `tags` format. Expected a comma-separated string or JSON array."
                    )
                return parsed
            return [tag.strip() for tag in stripped.split(",") if tag.strip()]
        raise ValueError(
            "Invalid `tags` format. Expected a comma-separated string or JSON array."
        )


class UpdateAssetsOperation(Operation):
    http_method = "PUT"
    payload_parameter = "json"
    input_model = UpdateAssetsParams

    def build_endpoint(self, parsed_input: UpdateAssetsParams) -> str:
        return f"{ASSETS_V2_BASE_URL}/{parsed_input.uuid}"

    def build_payload(self, parsed_input: UpdateAssetsParams) -> dict:
        params = parsed_input.model_dump()
        payload = {
            "atoms": self.payload_value(params, "atoms"),
            "category": self.payload_value(params, "category"),
            "criticality": self.payload_value(params, "criticality"),
            "description": self.payload_value(params, "description"),
            "entity_uuid": self.payload_value(params, "entity_uuid"),
            "name": self.payload_value(params, "name"),
            "props": self.payload_value(params, "props"),
            "reviewed": self.payload_value(params, "reviewed"),
            "revoked": self.payload_value(params, "revoked"),
            "tags": self.payload_value(params, "tags"),
            "type": self.payload_value(params, "type"),
        }
        return {key: value for key, value in payload.items() if value is not None}


def update_assets(config, params: dict):
    """Update a specific asset with v2 schema."""
    return UpdateAssetsOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
