from pydantic import AliasChoices, Field

from ...constants import ASSETS_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class GetAssetParams(InputModel):
    uuid: str = Field(validation_alias=AliasChoices("uuid", "asset_uuid"))
    with_telemetry: bool = False
    with_compliance: bool = False


class GetAssetOperation(Operation):
    http_method = "GET"
    payload_parameter = "params"
    input_model = GetAssetParams
    deprecated_aliases = DeprecatedAliases(single={"uuid": "asset_uuid"})

    def build_endpoint(self, parsed_input: GetAssetParams) -> str:
        return f"{ASSETS_V2_BASE_URL}/{parsed_input.uuid}"

    def build_payload(self, parsed_input: GetAssetParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "with_compliance": self.payload_value(
                params, "with_compliance", default=False
            ),
            "with_telemetry": self.payload_value(
                params, "with_telemetry", default=False
            ),
        }


def get_asset(config, params: dict):
    """Retrieve a specific asset."""
    return GetAssetOperation(api_action_cls=GenericAPIAction).execute(config, params)
