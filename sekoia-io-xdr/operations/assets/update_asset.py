from typing import Optional

from pydantic import field_validator

from ...constants import ASSETS_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class UpdateAssetParams(InputModel):
    asset_uuid: str
    asset_type_uuid: str
    asset_type_name: str
    asset_name: str
    asset_criticity: int
    asset_description: Optional[str] = None
    asset_attributes: Optional[list[str]] = None
    asset_keys: Optional[list[str]] = None
    asset_owners: Optional[list[str]] = None

    @field_validator("asset_attributes", "asset_keys", "asset_owners", mode="before")
    @classmethod
    def parse_csv_fields(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return list(value.split(",")) if value else []
        raise ValueError("Expected a comma-separated string or list.")


class UpdateAssetOperation(Operation):
    http_method = "PUT"
    payload_parameter = "json"
    input_model = UpdateAssetParams

    def build_endpoint(self, parsed_input: UpdateAssetParams) -> str:
        return f"{ASSETS_BASE_URL}/{parsed_input.asset_uuid}"

    def build_payload(self, parsed_input: UpdateAssetParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "asset_type": {
                "uuid": self.payload_value(params, "asset_type_uuid"),
                "name": self.payload_value(params, "asset_type_name"),
            },
            "attributes": self.payload_value(params, "asset_attributes"),
            "criticity": self.payload_value(params, "asset_criticity"),
            "description": self.payload_value(params, "asset_description", default=""),
            "keys": self.payload_value(params, "asset_keys"),
            "name": self.payload_value(params, "asset_name"),
            "owners": self.payload_value(params, "asset_owners"),
        }


def update_asset(config, params):
    """Update a specific asset."""
    return UpdateAssetOperation(api_action_cls=GenericAPIAction).execute(config, params)
